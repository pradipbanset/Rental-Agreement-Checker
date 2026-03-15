"""
Working Legal Document Scraper - Downloads PDFs and extracts text
These government sites provide PDFs which are easier to scrape than HTML
Updated to handle manually uploaded PDFs
"""

import os
import re
import time
from pathlib import Path
from typing import List, Dict, Optional
import requests
from bs4 import BeautifulSoup

# Check imports
try:
    from sentence_transformers import SentenceTransformer
    EMBEDDINGS_OK = True
except:
    print("⚠️  sentence-transformers not installed")
    EMBEDDINGS_OK = False

try:
    import chromadb
    CHROMADB_OK = True
except:
    print("⚠️  chromadb not installed")
    CHROMADB_OK = False

try:
    from playwright.sync_api import sync_playwright
    PLAYWRIGHT_OK = True
except:
    print("⚠️  playwright not installed")
    PLAYWRIGHT_OK = False

try:
    import PyPDF2
    PDF_OK = True
except:
    print("⚠️  PyPDF2 not installed (pip install PyPDF2)")
    PDF_OK = False


class WorkingLegalScraper:
    def __init__(self, base_dir="legal_documents", db_dir="vector_db"):
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(exist_ok=True)
        
        self.db_dir = Path(db_dir)
        self.db_dir.mkdir(exist_ok=True)
        
        # Direct PDF download links (the REAL way to get full text)
        self.sources = {
            "NSW": {
                "method": "playwright_expand",
                "url": "https://legislation.nsw.gov.au/view/whole/html/inforce/current/act-2010-042",
                "name": "Residential Tenancies Act 2010",
                "wait_selector": "div.fragment"
            },
            "VIC": {
                "method": "pdf_download", 
                "url": "https://www.legislation.vic.gov.au/in-force/acts/residential-tenancies-act-1997",
                "pdf_link_text": "authorised.pdf",
                "name": "Residential Tenancies Act 1997"
            },
            "QLD": {
                "method": "playwright_expand",
                "url": "https://www.legislation.qld.gov.au/view/whole/html/inforce/current/act-2008-073",
                "name": "Residential Tenancies and Rooming Accommodation Act 2008",
                "wait_selector": "div.Fragment"
            },
            "SA": {
                "method": "playwright_expand",
                "url": "https://www.legislation.sa.gov.au/LZ/C/A/RESIDENTIAL%20TENANCIES%20ACT%201995.aspx",
                "name": "Residential Tenancies Act 1995",
                "wait_selector": "div#content"
            },
            "WA": {
                "method": "pdf_download",
                "url": "https://www.legislation.wa.gov.au/legislation/statutes.nsf/main_mrtitle_826_homepage.html",
                "pdf_link_text": ".pdf",
                "name": "Residential Tenancies Act 1987"
            },
            "TAS": {
                "method": "playwright_expand",
                "url": "https://www.legislation.tas.gov.au/view/html/inforce/current/act-1997-082",
                "name": "Residential Tenancy Act 1997",
                "wait_selector": "main"
            }
        }
        
        if EMBEDDINGS_OK:
            print("📦 Loading embedding model...")
            self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        
        if CHROMADB_OK:
            print("🗄️  Initializing ChromaDB...")
            self.chroma_client = chromadb.PersistentClient(path=str(self.db_dir))
            self.collection = self.chroma_client.get_or_create_collection(
                name="australian_tenancy_laws",
                metadata={"description": "Australian residential tenancy legislation"}
            )
    
    def extract_text_from_pdf(self, pdf_path: Path) -> Optional[str]:
        """Extract text from a PDF file"""
        if not PDF_OK:
            print("❌ PyPDF2 not installed. Install: pip install PyPDF2")
            return None
        
        try:
            print(f"   📄 Extracting text from PDF: {pdf_path}")
            with open(pdf_path, 'rb') as f:
                reader = PyPDF2.PdfReader(f)
                text = ""
                for page in reader.pages:
                    text += page.extract_text() + "\n"
            
            # Clean text
            text = re.sub(r'\n{3,}', '\n\n', text)
            
            print(f"   ✅ Extracted {len(text):,} characters")
            return text
            
        except Exception as e:
            print(f"❌ Error extracting text from PDF: {e}")
            return None
    
    def check_for_manual_pdf(self, state: str) -> Optional[str]:
        """Check if a PDF was manually uploaded and extract its text"""
        pdf_path = self.base_dir / state / f"{state}_act.pdf"
        
        if pdf_path.exists():
            print(f"\n📁 Found manually uploaded PDF for {state}")
            text = self.extract_text_from_pdf(pdf_path)
            
            if text and len(text) > 10000:
                # Save extracted text
                txt_path = self.base_dir / state / f"{state}_act.txt"
                with open(txt_path, 'w', encoding='utf-8') as f:
                    f.write(text)
                print(f"   ✅ Saved extracted text to {txt_path}")
                return text
            elif text:
                print(f"   ⚠️  Extracted text too short ({len(text)} chars)")
                return None
        
        return None
    
    def download_pdf(self, state: str) -> Optional[str]:
        """Download and extract text from PDF"""
        if not PDF_OK:
            print("❌ PyPDF2 not installed. Install: pip install PyPDF2")
            return None
        
        config = self.sources[state]
        print(f"\n📥 Downloading {state} PDF...")
        
        try:
            # First, get the page to find PDF link
            response = requests.get(config["url"], timeout=30)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find PDF link
            pdf_link = None
            for link in soup.find_all('a', href=True):
                if config["pdf_link_text"] in link['href']:
                    pdf_link = link['href']
                    if not pdf_link.startswith('http'):
                        # Make absolute URL - FIX: ensure proper URL construction
                        from urllib.parse import urljoin
                        pdf_link = urljoin(config["url"], pdf_link)
                    break
            
            if not pdf_link:
                print(f"❌ Could not find PDF link on page")
                return None
            
            print(f"   Found PDF: {pdf_link}")
            
            # Download PDF
            pdf_response = requests.get(pdf_link, timeout=60)
            pdf_path = self.base_dir / state / f"{state}_act.pdf"
            pdf_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(pdf_path, 'wb') as f:
                f.write(pdf_response.content)
            
            print(f"   ✅ Downloaded: {pdf_path} ({len(pdf_response.content):,} bytes)")
            
            # Extract text from PDF
            text = self.extract_text_from_pdf(pdf_path)
            
            if text:
                # Save text
                txt_path = self.base_dir / state / f"{state}_act.txt"
                with open(txt_path, 'w', encoding='utf-8') as f:
                    f.write(text)
                return text
            
            return None
            
        except Exception as e:
            print(f"❌ Error downloading PDF: {e}")
            return None
    
    def scrape_with_playwright_expanded(self, state: str) -> Optional[str]:
        """Use Playwright to get FULL expanded view"""
        if not PLAYWRIGHT_OK:
            print("❌ Playwright not available")
            return None
        
        config = self.sources[state]
        url = config["url"]
        
        print(f"\n🌐 Scraping {state} with Playwright (expanded view)...")
        
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                context = browser.new_context(
                    user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                    viewport={'width': 1920, 'height': 1080}
                )
                
                page = context.new_page()
                print(f"   Loading {url}...")
                
                # Go to page
                page.goto(url, wait_until='networkidle', timeout=120000)
                
                # Wait for main content
                try:
                    page.wait_for_selector(config.get("wait_selector", "body"), timeout=30000)
                except:
                    pass
                
                print(f"   ⏳ Waiting for JavaScript to load all content...")
                page.wait_for_timeout(8000)
                
                # Try to click any "expand" or "view whole" buttons
                expand_selectors = [
                    "button:has-text('View whole')",
                    "a:has-text('View whole')",
                    "button:has-text('Expand')",
                    "[aria-expanded='false']"
                ]
                
                for selector in expand_selectors:
                    try:
                        elements = page.query_selector_all(selector)
                        for elem in elements[:3]:
                            elem.click()
                            page.wait_for_timeout(2000)
                            print(f"   ✅ Clicked expand button")
                    except:
                        pass
                
                # Scroll to load lazy content
                print(f"   📜 Scrolling to load all content...")
                for i in range(10):
                    page.evaluate("window.scrollBy(0, 5000)")
                    page.wait_for_timeout(500)
                
                # Get all text
                html = page.content()
                browser.close()
                
                # Parse
                soup = BeautifulSoup(html, 'html.parser')
                
                # Remove navigation/UI elements
                for element in soup(['script', 'style', 'nav', 'header', 'footer', 
                                    'button', 'form', 'iframe']):
                    element.decompose()
                
                # Get main content
                main_content = (
                    soup.find('div', class_='fragment') or 
                    soup.find('div', class_='Fragment') or
                    soup.find('main') or
                    soup.find('article') or
                    soup.find('body')
                )
                
                text = main_content.get_text(separator='\n', strip=True)
                text = re.sub(r'\n{3,}', '\n\n', text)
                text = re.sub(r' {2,}', ' ', text)
                
                print(f"   ✅ Extracted {len(text):,} characters")
                
                if len(text) > 10000:  # Got substantial content
                    txt_path = self.base_dir / state / f"{state}_act.txt"
                    txt_path.parent.mkdir(parents=True, exist_ok=True)
                    with open(txt_path, 'w', encoding='utf-8') as f:
                        f.write(text)
                    return text
                else:
                    print(f"   ⚠️  Content still too short")
                    return None
                    
        except Exception as e:
            print(f"❌ Playwright error: {e}")
            return None
    
    def scrape_state(self, state: str) -> Optional[str]:
        """Scrape a single state using the best method"""
        
        # First, check if we already have extracted text
        existing_txt = self.base_dir / state / f"{state}_act.txt"
        if existing_txt.exists():
            print(f"\n✅ {state} already scraped (text file exists)")
            with open(existing_txt, 'r', encoding='utf-8') as f:
                content = f.read()
            if len(content) > 10000:
                return content
            else:
                print(f"   ⚠️  Existing file too short, will try to re-process...")
        
        # Check for manually uploaded PDF
        manual_content = self.check_for_manual_pdf(state)
        if manual_content:
            return manual_content
        
        # If no manual PDF, try to scrape/download
        config = self.sources[state]
        method = config.get("method", "playwright_expand")
        
        if method == "pdf_download":
            content = self.download_pdf(state)
        else:  # playwright_expand
            content = self.scrape_with_playwright_expanded(state)
        
        if content and len(content) > 10000:
            print(f"   ✅ Successfully scraped {state}: {len(content):,} chars")
            return content
        else:
            print(f"   ❌ Failed to scrape {state}")
            return None
    
    def chunk_text(self, text: str, chunk_size: int = 1000, overlap: int = 200) -> List[str]:
        """Split text into overlapping chunks"""
        sentences = re.split(r'(?<=[.!?])\s+', text)
        chunks = []
        current_chunk = []
        current_size = 0
        
        for sentence in sentences:
            sentence_len = len(sentence.split())
            if current_size + sentence_len > chunk_size and current_chunk:
                chunks.append(' '.join(current_chunk))
                # Keep last 2 sentences for overlap
                overlap_sentences = current_chunk[-2:] if len(current_chunk) > 2 else current_chunk
                current_chunk = overlap_sentences + [sentence]
                current_size = sum(len(s.split()) for s in current_chunk)
            else:
                current_chunk.append(sentence)
                current_size += sentence_len
        
        if current_chunk:
            chunks.append(' '.join(current_chunk))
        
        return chunks
    
    def scrape_all_and_load(self):
        """Scrape all states and load into vector DB"""
        
        if not (EMBEDDINGS_OK and CHROMADB_OK):
            print("\n❌ Cannot load to vector DB - missing dependencies")
            print("Install: pip install sentence-transformers chromadb pydantic")
            return
        
        print("\n" + "="*60)
        print("🚀 SCRAPING ALL AUSTRALIAN STATES")
        print("="*60)
        
        successful = []
        failed = []
        doc_id = 0
        
        for state in self.sources.keys():
            print(f"\n{'='*60}")
            print(f"Processing {state}")
            print(f"{'='*60}")
            
            content = self.scrape_state(state)
            
            if not content:
                failed.append(state)
                continue
            
            successful.append(state)
            
            # Chunk and embed
            print(f"   🔪 Chunking text...")
            chunks = self.chunk_text(content)
            print(f"   ✅ Created {len(chunks)} chunks")
            
            # Add to vector DB
            print(f"   💾 Adding to vector database...")
            for i, chunk in enumerate(chunks):
                if len(chunk.strip()) < 50:
                    continue
                
                embedding = self.embedding_model.encode(chunk).tolist()
                
                self.collection.add(
                    embeddings=[embedding],
                    documents=[chunk],
                    metadatas=[{"state": state, "chunk_id": i}],
                    ids=[f"{state}_{doc_id}"]
                )
                doc_id += 1
            
            print(f"   ✅ Added {len(chunks)} chunks to database")
        
        # Summary
        print(f"\n{'='*60}")
        print("📊 FINAL SUMMARY")
        print(f"{'='*60}")
        
        if successful:
            print(f"✅ Successfully scraped: {', '.join(successful)}")
            print(f"💾 Total chunks in database: {doc_id}")
            print(f"📁 Database: {self.db_dir.absolute()}")
        
        if failed:
            print(f"\n❌ Failed: {', '.join(failed)}")
            print(f"\nFor failed states, you can:")
            print(f"1. Manually download PDFs and place them in:")
            print(f"   legal_documents/STATE/STATE_act.pdf")
            print(f"   (e.g., legal_documents/VIC/VIC_act.pdf)")
            print(f"2. Then run the script again - it will automatically process them!")
        
        if successful:
            print(f"\n✅ RAG System is ready to use!")
            self.test_query()
    
    def test_query(self):
        """Test the system with a query"""
        if not (EMBEDDINGS_OK and CHROMADB_OK):
            return
        
        print(f"\n{'='*60}")
        print("🧪 Testing RAG System")
        print(f"{'='*60}")
        
        query = "What is the maximum bond amount?"
        print(f"\nQuery: {query}\n")
        
        query_embedding = self.embedding_model.encode(query).tolist()
        
        for state in self.sources.keys():
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=1,
                where={"state": state}
            )
            
            if results['documents'] and results['documents'][0]:
                print(f"{state} Result:")
                print(results['documents'][0][0][:300] + "...")
                print()
            else:
                print(f"{state}: No results")


def main():
    print("🏛️  Australian Tenancy Laws - Working Scraper")
    print("="*60)
    print("\nThis scraper will:")
    print("1. Check for manually uploaded PDFs first")
    print("2. Try to download/scrape if no manual PDF exists")
    print("3. Extract text from PDFs and load into vector database")
    print()
    print("💡 Tip: If scraping fails, manually download PDFs and place them in:")
    print("   legal_documents/STATE/STATE_act.pdf")
    print("   Then run this script again!")
    print()
    
    # Check dependencies
    missing = []
    if not EMBEDDINGS_OK:
        missing.append("sentence-transformers")
    if not CHROMADB_OK:
        missing.append("chromadb")
    if not PLAYWRIGHT_OK:
        missing.append("playwright")
    if not PDF_OK:
        missing.append("PyPDF2")
    
    if missing:
        print("⚠️  Missing dependencies:")
        for dep in missing:
            print(f"   - {dep}")
        print(f"\nInstall: pip install {' '.join(missing)}")
        if "playwright" in missing:
            print("Then run: playwright install chromium")
        print()
    
    input("Press Enter to start scraping...")
    
    scraper = WorkingLegalScraper()
    scraper.scrape_all_and_load()


if __name__ == "__main__":
    main()