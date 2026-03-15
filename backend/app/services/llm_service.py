"""
LLM Service - Handles all LLM interactions
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))

from agent.llm_adapters import ClaudeLLMAdapter, MockLLMAdapter
from app.core.config import settings

class LLMService:
    def __init__(self):
        """Initialize LLM adapter"""
        try:
            self.llm = ClaudeLLMAdapter(api_key=settings.CLAUDE_API_KEY)
            print("✓ Using ClaudeLLMAdapter")
        except Exception as e:
            print(f"⚠ Claude unavailable ({e}), falling back to MockLLMAdapter")
            self.llm = MockLLMAdapter()
    
    def analyze_contract(self, text: str) -> dict:
        """
        Analyze contract text and extract clauses
        
        Args:
            text: Contract text to analyze
            
        Returns:
            Analysis results with clauses
        """
        return self.llm.generate(
            prompt="Analyze rental contract",
            input_text=text
        )
    
    def chat(self, prompt: str, context: dict) -> str:
        """
        Generate chat response with context
        
        Args:
            prompt: User's question
            context: Dictionary containing contract info, legal references, etc.
            
        Returns:
            LLM response text
        """
        smart_prompt = self._build_chat_prompt(prompt, context)
        return self.llm.query(smart_prompt)
    
    def _build_chat_prompt(self, prompt: str, context: dict) -> str:
        """Build a smart prompt combining contract and legal context"""
        
        contract_excerpt = context.get('contract_excerpt', '')
        legal_context = context.get('legal_context', '')
        state = context.get('state', 'NSW')
        filename = context.get('filename', 'Unknown')
        num_clauses = context.get('num_clauses', 0)
        high_risk = context.get('high_risk', 0)
        medium_risk = context.get('medium_risk', 0)
        illegal = context.get('illegal', 0)
        
        return f"""You are an intelligent Australian Rental Fairness Checker assistant.

CONTRACT INFORMATION:
Filename: {filename}
State: {state}
Analysis: {num_clauses} clauses | {high_risk} high-risk | {medium_risk} medium-risk | {illegal} illegal

CONTRACT EXCERPT (what the user uploaded):
{contract_excerpt}

{legal_context}

USER QUESTION: {prompt}

INSTRUCTIONS:
1. Answer the user's question by analyzing BOTH the contract excerpt above AND the legal references
2. When citing laws, reference [LAW 1], [LAW 2], etc. from the legal references section
3. If the legal references don't cover the topic, use your knowledge of {state} tenancy law but clearly state "based on general {state} tenancy law knowledge"
4. Be conversational, helpful, and practical
5. Explain in simple terms
6. If the question is incomplete or unclear, make a reasonable interpretation and provide a helpful answer

Provide a clear, helpful answer (2-4 paragraphs):"""

# Singleton instance
llm_service = LLMService()