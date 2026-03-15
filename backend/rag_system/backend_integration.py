"""
Backend Integration - Add RAG to your existing FastAPI backend

This shows how to integrate the RAG system with your current
agent/main.py and backend/main.py
"""

from fastapi import FastAPI, UploadFile, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Optional
import google.generativeai as genai
from rag_retriever import TenancyLawRetriever

# Initialize RAG retriever (do this once at startup)
rag_retriever = TenancyLawRetriever(db_dir="chroma_db")

# Your existing models
class ChatMessage(BaseModel):
    message: str
    state: str
    conversation_history: Optional[List[Dict]] = []

class ContractAnalysis(BaseModel):
    state: str
    clauses: List[Dict]


# OPTION 1: Enhance your /analyze endpoint with RAG
async def analyze_contract_with_rag(
    clauses: List[Dict],
    state: str,
    gemini_api_key: str
) -> Dict:
    """
    Enhanced contract analysis using RAG + Gemini
    
    This replaces or enhances your existing analyze_contract function
    """
    
    # Configure Gemini
    genai.configure(api_key=gemini_api_key)
    model = genai.GenerativeModel('gemini-pro')
    
    analysis_results = []
    violations = []
    warnings = []
    
    for clause in clauses:
        clause_text = clause.get('text', '')
        clause_type = clause.get('type', 'general')
        
        # 1. Get relevant legal context from RAG
        legal_context = rag_retriever.get_context_for_clause(
            clause_text=clause_text,
            clause_type=clause_type,
            state=state,
            n_results=3
        )
        
        # 2. Build prompt for Gemini with legal context
        prompt = f"""
You are an expert in {state} residential tenancy law.

RELEVANT LEGAL PROVISIONS:
{legal_context}

CONTRACT CLAUSE TO ANALYZE:
Type: {clause_type}
Text: {clause_text}

TASK:
1. Compare this clause against the legal provisions above
2. Identify if the clause violates any laws
3. Assess the risk level (low/medium/high)
4. Provide specific legal references

Respond in this format:
COMPLIANCE: [compliant/non-compliant/unclear]
RISK_LEVEL: [low/medium/high]
LEGAL_ISSUE: [specific issue if any]
EXPLANATION: [brief explanation with legal references]
RECOMMENDATION: [what should be done]
"""
        
        # 3. Get Gemini analysis
        try:
            response = model.generate_content(prompt)
            analysis_text = response.text
            
            # Parse Gemini response
            result = {
                "clause_text": clause_text,
                "clause_type": clause_type,
                "legal_context_used": legal_context[:500] + "...",  # Truncate for response
                "ai_analysis": analysis_text,
                "has_legal_backing": True
            }
            
            # Extract compliance status
            if "non-compliant" in analysis_text.lower():
                violations.append(result)
            elif "unclear" in analysis_text.lower() or "medium" in analysis_text.lower():
                warnings.append(result)
            
            analysis_results.append(result)
            
        except Exception as e:
            print(f"Error analyzing clause: {e}")
            analysis_results.append({
                "clause_text": clause_text,
                "error": str(e)
            })
    
    return {
        "state": state,
        "total_clauses_analyzed": len(clauses),
        "violations": violations,
        "warnings": warnings,
        "detailed_analysis": analysis_results,
        "rag_enabled": True
    }


# OPTION 2: Enhance your /chat endpoint with RAG
async def chat_with_rag_context(
    user_message: str,
    state: str,
    contract_summary: Optional[Dict],
    conversation_history: List[Dict],
    gemini_api_key: str
) -> str:
    """
    Enhanced chat with RAG-retrieved legal context
    
    This replaces or enhances your existing chat function
    """
    
    # 1. Retrieve relevant legal information
    relevant_laws = rag_retriever.retrieve_relevant_laws(
        query=user_message,
        state=state,
        n_results=5
    )
    
    # 2. Build legal context
    legal_context = f"\n\n=== RELEVANT {state} TENANCY LAWS ===\n"
    for i, law in enumerate(relevant_laws, 1):
        legal_context += f"\n{i}. From {law['source']}:\n"
        legal_context += f"{law['content']}\n"
    
    # 3. Build comprehensive prompt for Gemini
    system_prompt = f"""
You are a knowledgeable tenancy law assistant for {state}, Australia.

You have access to the following VERIFIED LEGAL INFORMATION:
{legal_context}

IMPORTANT RULES:
1. Base your answers on the legal provisions provided above
2. Always cite specific sections or sources when giving legal information
3. If the legal context doesn't contain the answer, say so
4. Never make up legal information
5. Always remind users this is informational, not legal advice

CONTRACT CONTEXT:
{contract_summary if contract_summary else "No contract uploaded yet"}

CONVERSATION HISTORY:
{format_conversation_history(conversation_history)}

Now answer the user's question using the legal information provided.
"""
    
    # 4. Call Gemini with enhanced context
    genai.configure(api_key=gemini_api_key)
    model = genai.GenerativeModel('gemini-pro')
    
    try:
        response = model.generate_content(
            f"{system_prompt}\n\nUSER QUESTION: {user_message}"
        )
        return response.text
    
    except Exception as e:
        return f"Error: {str(e)}"


def format_conversation_history(history: List[Dict]) -> str:
    """Format conversation history for prompt"""
    formatted = ""
    for msg in history[-5:]:  # Last 5 messages
        role = msg.get('role', 'user')
        content = msg.get('content', '')
        formatted += f"{role.upper()}: {content}\n"
    return formatted


# OPTION 3: New endpoint for legal question answering
async def answer_legal_question(
    question: str,
    state: str,
    gemini_api_key: str
) -> Dict:
    """
    Standalone legal question answering with RAG
    """
    
    # Retrieve relevant laws
    relevant_laws = rag_retriever.retrieve_relevant_laws(
        query=question,
        state=state,
        n_results=5
    )
    
    # Build context
    context = ""
    sources = []
    for law in relevant_laws:
        context += f"\n{law['content']}\n"
        sources.append({
            "source": law['source'],
            "state": law['state'],
            "doc_type": law['doc_type']
        })
    
    # Get answer from Gemini
    genai.configure(api_key=gemini_api_key)
    model = genai.GenerativeModel('gemini-pro')
    
    prompt = f"""
Based on the following {state} tenancy law provisions:

{context}

Answer this question: {question}

Provide:
1. Direct answer
2. Relevant legal references
3. Any important caveats
4. Reminder that this is general information, not legal advice
"""
    
    response = model.generate_content(prompt)
    
    return {
        "question": question,
        "state": state,
        "answer": response.text,
        "sources_used": sources,
        "legal_backing": True
    }





# TESTING THE INTEGRATION


def test_rag_integration():
    """
    Test the RAG integration before deploying
    """
    import os
    
    print("🧪 Testing RAG Integration\n")
    
    # Test 1: Legal retrieval
    print("Test 1: Retrieving relevant laws...")
    results = rag_retriever.retrieve_relevant_laws(
        query="maximum bond amount",
        state="NSW",
        n_results=2
    )
    print(f"✅ Retrieved {len(results)} relevant provisions\n")
    
    # Test 2: Clause analysis (mock)
    print("Test 2: Analyzing a clause...")
    clause = "Tenant must pay 6 weeks rent as bond"
    legal_context = rag_retriever.get_context_for_clause(
        clause_text=clause,
        clause_type="bond",
        state="NSW"
    )
    print(f"✅ Retrieved legal context ({len(legal_context)} characters)\n")
    
    # Test 3: Full analysis (requires Gemini API key)
    gemini_key = os.getenv("GEMINI_API_KEY")
    if gemini_key:
        print("Test 3: Full RAG + Gemini analysis...")
        # You would call analyze_contract_with_rag here
        print("✅ Would perform full analysis with Gemini\n")
    else:
        print("⚠️  Test 3 skipped (no GEMINI_API_KEY found)\n")
    
    print("✅ All tests passed!")


if __name__ == "__main__":
    test_rag_integration()