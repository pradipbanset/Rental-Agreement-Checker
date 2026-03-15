"""
Vector Database Loader - Loads legal documents into ChromaDB
Processes PDFs, text files, and creates embeddings for RAG
"""

import os
from pathlib import Path
from typing import List, Dict
import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
import PyPDF2

class LegalDocumentLoader:
    def __init__(
        self, 
        docs_dir="legal_documents",
        db_dir="chroma_db",
        collection_name="tenancy_laws"
    ):
        self.docs_dir = Path(docs_dir)
        self.db_dir = Path(db_dir)
        
        # Initialize ChromaDB client
        self.client = chromadb.PersistentClient(
            path=str(self.db_dir),
            settings=Settings(anonymized_telemetry=False)
        )
        
        # Load embedding model (free, runs locally)
        print("📥 Loading embedding model (first time may take a moment)...")
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        print("✅ Embedding model loaded")
        
        # Get or create collection
        try:
            self.collection = self.client.get_collection(collection_name)
            print(f"📚 Using existing collection: {collection_name}")
        except:
            self.collection = self.client.create_collection(
                name=collection_name,
                metadata={"description": "Australian tenancy law documents"}
            )
            print(f"✨ Created new collection: {collection_name}")
    
    def extract_text_from_pdf(self, pdf_path: Path) -> str:
        """Extract text from PDF file"""
        try:
            with open(pdf_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                text = ""
                for page in reader.pages:
                    text += page.extract_text() + "\n"
                return text
        except Exception as e:
            print(f"⚠️  Error reading PDF {pdf_path}: {e}")
            return ""
    
    def extract_text_from_txt(self, txt_path: Path) -> str:
        """Extract text from text file"""
        try:
            with open(txt_path, 'r', encoding='utf-8') as file:
                return file.read()
        except Exception as e:
            print(f"⚠️  Error reading TXT {txt_path}: {e}")
            return ""
    
    def chunk_text(self, text: str, chunk_size: int = 1000, overlap: int = 200) -> List[str]:
        """
        Split text into overlapping chunks for better context retrieval
        
        Args:
            text: Full text to chunk
            chunk_size: Target size of each chunk in characters
            overlap: Number of characters to overlap between chunks
        """
        if not text or len(text) < chunk_size:
            return [text] if text else []
        
        chunks = []
        start = 0
        
        while start < len(text):
            end = start + chunk_size
            
            # Try to break at sentence end
            if end < len(text):
                # Look for sentence endings near the chunk boundary
                sentence_ends = ['. ', '.\n', '? ', '! ']
                best_break = end
                
                for ending in sentence_ends:
                    pos = text.rfind(ending, start + chunk_size - 200, end)
                    if pos != -1 and pos > start:
                        best_break = pos + len(ending)
                        break
                
                end = best_break
            
            chunk = text[start:end].strip()
            if chunk:
                chunks.append(chunk)
            
            start = end - overlap if end < len(text) else len(text)
        
        return chunks
    
    def load_documents(self):
        """Load all documents from legal_documents directory"""
        
        if not self.docs_dir.exists():
            print(f"❌ Directory not found: {self.docs_dir}")
            print("   Run the document collector script first!")
            return
        
        all_documents = []
        all_metadatas = []
        all_ids = []
        
        doc_count = 0
        
        # Process each state directory
        for state_dir in self.docs_dir.iterdir():
            if not state_dir.is_dir():
                continue
            
            state = state_dir.name
            print(f"\n📂 Processing {state} documents...")
            
            # Process all files in state directory
            for file_path in state_dir.rglob('*'):
                if not file_path.is_file():
                    continue
                
                # Skip README and hidden files
                if file_path.name.startswith('.') or file_path.name == 'README.md':
                    continue
                
                print(f"   📄 Processing: {file_path.name}")
                
                # Extract text based on file type
                if file_path.suffix.lower() == '.pdf':
                    text = self.extract_text_from_pdf(file_path)
                    doc_type = "legislation_pdf"
                elif file_path.suffix.lower() == '.txt':
                    text = self.extract_text_from_txt(file_path)
                    doc_type = "provisions_summary"
                else:
                    print(f"      ⏭️  Skipping unsupported file type: {file_path.suffix}")
                    continue
                
                if not text or len(text.strip()) < 100:
                    print(f"      ⚠️  No text extracted or text too short")
                    continue
                
                # Chunk the text
                chunks = self.chunk_text(text)
                print(f"      ✂️  Created {len(chunks)} chunks")
                
                # Add each chunk to the collection
                for i, chunk in enumerate(chunks):
                    doc_id = f"{state}_{file_path.stem}_chunk_{i}"
                    
                    metadata = {
                        "state": state,
                        "source_file": file_path.name,
                        "doc_type": doc_type,
                        "chunk_index": i,
                        "total_chunks": len(chunks)
                    }
                    
                    all_documents.append(chunk)
                    all_metadatas.append(metadata)
                    all_ids.append(doc_id)
                    doc_count += 1
        
        if not all_documents:
            print("\n❌ No documents found to load!")
            print("   Make sure you have .txt or .pdf files in the legal_documents directory")
            return
        
        # Add documents to ChromaDB in batches
        print(f"\n💾 Adding {doc_count} document chunks to vector database...")
        batch_size = 100
        
        for i in range(0, len(all_documents), batch_size):
            batch_docs = all_documents[i:i+batch_size]
            batch_meta = all_metadatas[i:i+batch_size]
            batch_ids = all_ids[i:i+batch_size]
            
            # Generate embeddings
            embeddings = self.embedding_model.encode(batch_docs).tolist()
            
            # Add to ChromaDB
            self.collection.add(
                documents=batch_docs,
                embeddings=embeddings,
                metadatas=batch_meta,
                ids=batch_ids
            )
            
            print(f"   ✅ Processed batch {i//batch_size + 1}/{(len(all_documents)-1)//batch_size + 1}")
        
        print(f"\n🎉 Successfully loaded {doc_count} document chunks!")
        print(f"   Database location: {self.db_dir.absolute()}")
    
    def test_retrieval(self, query: str = "What is the maximum bond amount?", n_results: int = 3):
        """Test the retrieval system with a sample query"""
        
        print(f"\n🔍 Testing retrieval with query: '{query}'")
        
        # Generate query embedding
        query_embedding = self.embedding_model.encode([query]).tolist()
        
        # Search the collection
        results = self.collection.query(
            query_embeddings=query_embedding,
            n_results=n_results
        )
        
        print(f"\n📋 Top {n_results} results:")
        print("=" * 80)
        
        for i, (doc, metadata) in enumerate(zip(results['documents'][0], results['metadatas'][0])):
            print(f"\nResult {i+1}:")
            print(f"State: {metadata['state']}")
            print(f"Source: {metadata['source_file']}")
            print(f"Chunk: {metadata['chunk_index'] + 1}/{metadata['total_chunks']}")
            print(f"\nContent preview (first 300 chars):")
            print(doc[:300] + "..." if len(doc) > 300 else doc)
            print("-" * 80)

def main():
    print("🏛️  Legal Documents Vector Database Loader")
    print("=" * 60)
    
    loader = LegalDocumentLoader()
    
    print("\n📚 Loading documents into vector database...")
    loader.load_documents()
    
    # Test the system
    print("\n" + "=" * 60)
    loader.test_retrieval("What is the maximum bond amount in NSW?")
    
    print("\n" + "=" * 60)
    print("✅ Setup complete! Your RAG system is ready.")
    print("\nNext steps:")
    print("1. Test queries with different questions")
    print("2. Integrate with your main application")
    print("3. Add more documents as needed")

if __name__ == "__main__":
    main()