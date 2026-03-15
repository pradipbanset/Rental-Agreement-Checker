"""
RAG Service - Handles retrieval of legal documents
"""
import sys
import os
from functools import lru_cache
sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))

from app.core.config import settings

try:
    from rag_system.rag_retriever import TenancyLawRetriever
    RAG_AVAILABLE = True
    print("✓ RAG system imported successfully")
except ImportError as e:
    RAG_AVAILABLE = False
    print(f"⚠ RAG system not available: {e}")

class RAGService:
    def __init__(self):
        """Initialize RAG retriever"""
        self.retriever = None
        
        if RAG_AVAILABLE:
            try:
                self.retriever = TenancyLawRetriever(
                    db_dir=settings.RAG_DB_DIR,
                    collection_name=settings.RAG_COLLECTION_NAME
                )
                print("✓ RAG retriever initialized")
            except Exception as e:
                print(f"⚠ RAG initialization failed: {e}")
    
    @lru_cache(maxsize=200)
    def retrieve_laws(self, query: str, state: str, n_results: int = 3) -> list:
        """
        Retrieve relevant laws from vector database (cached)
        
        Args:
            query: User's question
            state: State/territory code
            n_results: Number of results to return
            
        Returns:
            List of relevant law documents
        """
        if not self.retriever:
            return []
        
        try:
            return self.retriever.retrieve_relevant_laws(
                query=query,
                state=state,
                n_results=n_results
            )
        except Exception as e:
            print(f"⚠ RAG query error: {e}")
            return []
    
    def format_legal_context(self, query: str, state: str, n_results: int = 3) -> str:
        """
        Retrieve and format legal context for LLM
        
        Args:
            query: User's question
            state: State/territory code
            n_results: Number of results to retrieve
            
        Returns:
            Formatted legal context string
        """
        print(f"🔍 RAG Query: {query} ({state})")
        
        relevant_laws = self.retrieve_laws(query, state, n_results)
        
        if not relevant_laws:
            print(f"⚠ No relevant laws found for: {query}")
            return ""
        
        legal_context = "\n=== LEGAL REFERENCES (from your scraped laws database) ===\n"
        for i, law in enumerate(relevant_laws, 1):
            legal_context += f"\n[LAW {i}] {state} - {law['source']}:\n"
            legal_context += f"{law['content'][:500]}\n"
        
        print(f"✓ Retrieved {len(relevant_laws)} relevant laws from vector DB")
        return legal_context

# Singleton instance
rag_service = RAGService()