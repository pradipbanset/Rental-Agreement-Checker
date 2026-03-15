"""
RAG Retriever - Integrates with  existing tenancy agent
Retrieves relevant legal context for contract analysis
"""

import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
from typing import List, Dict, Optional

class TenancyLawRetriever:
    """
    Retrieves relevant legal information for tenancy contract analysis
    """
    
    def __init__(
        self,
        db_dir: str = "chroma_db",
        collection_name: str = "tenancy_laws",
        model_name: str = 'all-MiniLM-L6-v2'
    ):
        """
        Initialize the RAG retriever
        
        Args:
            db_dir: Path to ChromaDB database
            collection_name: Name of the collection to use
            model_name: SentenceTransformer model name
        """
        self.client = chromadb.PersistentClient(
            path=db_dir,
            settings=Settings(anonymized_telemetry=False)
        )
        
        self.collection = self.client.get_or_create_collection(
          name=collection_name,
          metadata={"description": "Tenancy law embeddings"})
        self.embedding_model = SentenceTransformer(model_name)
    
    def retrieve_relevant_laws(
        self,
        query: str,
        state: Optional[str] = None,
        n_results: int = 5
    ) -> List[Dict]:
        """
        Retrieve relevant legal provisions based on a query
        
        Args:
            query: The question or clause to find relevant laws for
            state: Optional state filter (NSW, VIC, QLD, etc.)
            n_results: Number of results to return
            
        Returns:
            List of relevant legal provisions with metadata
        """
        # Generate query embedding
        query_embedding = self.embedding_model.encode([query]).tolist()
        
        # Build filter for state if provided
        where_filter = {"state": state} if state else None
        
        # Search the collection
        results = self.collection.query(
            query_embeddings=query_embedding,
            n_results=n_results,
            where=where_filter
        )
        
        # Format results
        formatted_results = []
        for doc, metadata in zip(results['documents'][0], results['metadatas'][0]):
            formatted_results.append({
                "content": doc,
                "state": metadata['state'],
                "source": metadata['source_file'],
                "doc_type": metadata['doc_type']
            })
        
        return formatted_results
    
    def get_context_for_clause(
        self,
        clause_text: str,
        clause_type: str,
        state: str,
        n_results: int = 3
    ) -> str:
        """
        Get relevant legal context for a specific contract clause
        
        Args:
            clause_text: The contract clause text
            clause_type: Type of clause (e.g., "bond", "rent_increase", "repairs")
            state: State jurisdiction
            n_results: Number of relevant provisions to retrieve
            
        Returns:
            Formatted legal context string
        """
        # Create enhanced query combining clause text and type
        query = f"{clause_type}: {clause_text}"
        
        # Retrieve relevant laws
        results = self.retrieve_relevant_laws(query, state, n_results)
        
        if not results:
            return f"No specific legal provisions found for {state} regarding {clause_type}."
        
        # Format context
        context = f"Relevant {state} Tenancy Law Provisions:\n\n"
        
        for i, result in enumerate(results, 1):
            context += f"--- Provision {i} (from {result['source']}) ---\n"
            context += f"{result['content']}\n\n"
        
        return context
    
    def analyze_clause_legality(
        self,
        clause_text: str,
        clause_type: str,
        state: str
    ) -> Dict:
        """
        Analyze a clause against relevant laws
        
        Args:
            clause_text: The contract clause to analyze
            clause_type: Type of clause
            state: State jurisdiction
            
        Returns:
            Dictionary with analysis results
        """
        # Get relevant legal context
        legal_context = self.get_context_for_clause(
            clause_text, clause_type, state, n_results=3
        )
        
        # Get the raw results for additional processing
        query = f"{clause_type}: {clause_text}"
        results = self.retrieve_relevant_laws(query, state, n_results=3)
        
        return {
            "clause": clause_text,
            "clause_type": clause_type,
            "state": state,
            "legal_context": legal_context,
            "relevant_provisions": results
        }
    
    def get_state_overview(self, state: str) -> str:
        """
        Get a general overview of tenancy laws for a state
        
        Args:
            state: State code (NSW, VIC, QLD, etc.)
            
        Returns:
            Overview of key provisions
        """
        # Retrieve general provisions
        key_topics = [
            "bond provisions",
            "rent increase rules",
            "repairs and maintenance",
            "lease termination"
        ]
        
        overview = f"{state} Tenancy Law Overview:\n\n"
        
        for topic in key_topics:
            results = self.retrieve_relevant_laws(topic, state, n_results=1)
            if results:
                overview += f"=== {topic.upper()} ===\n"
                overview += f"{results[0]['content'][:500]}...\n\n"
        
        return overview


# Integration example with your existing agent
class EnhancedTenancyAgent:
    """
    Enhanced version of your tenancy agent with RAG integration
    """
    
    def __init__(self, rag_retriever: TenancyLawRetriever):
        self.retriever = rag_retriever
    
    def analyze_contract_with_rag(
        self,
        clauses: List[Dict],
        state: str
    ) -> Dict:
        """
        Analyze contract clauses with RAG-enhanced legal context
        
        Args:
            clauses: List of extracted clauses from contract
            state: State jurisdiction
            
        Returns:
            Analysis results with legal backing
        """
        analysis_results = []
        
        for clause in clauses:
            clause_text = clause.get('text', '')
            clause_type = clause.get('type', 'general')
            
            # Get relevant legal context
            analysis = self.retriever.analyze_clause_legality(
                clause_text, clause_type, state
            )
            
            # Add to results
            analysis_results.append({
                "clause": clause_text,
                "type": clause_type,
                "legal_context": analysis['legal_context'],
                "provisions_found": len(analysis['relevant_provisions'])
            })
        
        return {
            "state": state,
            "total_clauses": len(clauses),
            "clause_analyses": analysis_results
        }
    
    def chat_with_legal_context(
        self,
        user_question: str,
        state: str,
        contract_context: Optional[Dict] = None
    ) -> str:
        """
        Answer user questions with RAG-retrieved legal context
        
        Args:
            user_question: User's question
            state: State jurisdiction
            contract_context: Optional contract information
            
        Returns:
            Answer with legal backing
        """
        # Retrieve relevant laws for the question
        relevant_laws = self.retriever.retrieve_relevant_laws(
            user_question, state, n_results=3
        )
        
        # Build context for LLM
        legal_context = "Relevant Legal Information:\n\n"
        for i, law in enumerate(relevant_laws, 1):
            legal_context += f"{i}. From {law['source']}:\n"
            legal_context += f"{law['content']}\n\n"
        
        # Here you would pass this to your LLM (Gemini)
        # For now, return the context
        response = f"""
Based on {state} tenancy law:

{legal_context}

Answer to your question: "{user_question}"
[Your LLM would generate an answer here using the above legal context]
"""
        
        return response


# Usage example
def example_usage():
    """Example of how to use the RAG retriever"""
    
    print("🔧 Initializing RAG Retriever...")
    retriever = TenancyLawRetriever(db_dir="chroma_db")
    
    # Example 1: Simple query
    print("\n📝 Example 1: Retrieve relevant laws")
    results = retriever.retrieve_relevant_laws(
        query="What is the maximum bond amount?",
        state="NSW",
        n_results=2
    )
    
    for result in results:
        print(f"\nState: {result['state']}")
        print(f"Source: {result['source']}")
        print(f"Content: {result['content'][:200]}...")
    
    # Example 2: Analyze a clause
    print("\n📝 Example 2: Analyze a contract clause")
    clause = "Tenant must pay 6 weeks rent as bond deposit"
    analysis = retriever.analyze_clause_legality(
        clause_text=clause,
        clause_type="bond",
        state="NSW"
    )
    
    print(f"\nClause: {clause}")
    print(f"State: {analysis['state']}")
    print(f"\nLegal Context:\n{analysis['legal_context'][:500]}...")
    
    # Example 3: Use with enhanced agent
    print("\n📝 Example 3: Enhanced Agent")
    agent = EnhancedTenancyAgent(retriever)
    
    response = agent.chat_with_legal_context(
        user_question="Can my landlord increase rent twice in one year?",
        state="NSW"
    )
    
    print(response)


if __name__ == "__main__":
    example_usage()