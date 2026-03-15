from typing import Dict, Any
import time
import re
import os
import requests
import json

class LLMAdapter:
    def generate(self, prompt: str, *, input_text: str = "") -> Dict[str, Any]:
        raise NotImplementedError("Implement in subclass")
    
    def query(self, prompt: str) -> str:
        """
        Simple text-to-text query method for chat/conversational use.
        """
        raise NotImplementedError("Implement in subclass")

class MockLLMAdapter(LLMAdapter):
    """
    Mock LLM that splits text into clauses, detects numeric values,
    and classifies clause types using keyword matching.
    """
    def generate(self, prompt: str, *, input_text: str = "") -> Dict[str, Any]:
        paragraphs = [p.strip() for p in input_text.split("\n\n") if p.strip()]
        clauses = []
        cid = 1
        
        for p in paragraphs:
            lower_p = p.lower()
            
            # CLAUSE TYPE CLASSIFICATION
            clause_type = self._classify_clause_type(lower_p)
            
            # NUMERIC EXTRACTION 
            numeric_values = {}
            
            # ✅ FIX: Better blank field detection
            is_blank_dollar_field = bool(re.search(r'\$\s*[._\s]{2,}', p))
            
            # Extract dollar amounts ONLY if not a blank field
            if not is_blank_dollar_field:
                amounts = re.findall(r'\$\s*(\d{1,}(?:,\d{3})*(?:\.\d{2})?)', p)
                if amounts:
                    cleaned_amounts = [float(a.replace(',', '')) for a in amounts]
                    if cleaned_amounts:
                        numeric_values["amount"] = cleaned_amounts[0]
            
            # ✅ FIX: Mark financial clauses with missing amounts
            if "amount" not in numeric_values:
                financial_keywords = ["bond", "rent", "deposit", "payment", "fee", "charge"]
                if any(keyword in lower_p for keyword in financial_keywords):
                    numeric_values["amount"] = None
                    numeric_values["amount_status"] = "not_specified"
            
            # Extract weeks
            weeks_matches = re.findall(r'(\d+)\s*weeks?', lower_p)
            if weeks_matches:
                numeric_values["weeks"] = int(weeks_matches[0])
            
            # Extract days (for notice periods)
            days_matches = re.findall(r'(\d+)\s*days?', lower_p)
            if days_matches:
                numeric_values["days"] = int(days_matches[0])
            
            # Extract months
            months_matches = re.findall(r'(\d+)\s*months?', lower_p)
            if months_matches:
                numeric_values["months"] = int(months_matches[0])
            
            # Preliminary risk assessment
            soft_risk = "low"
            high_risk_keywords = ["penalty", "forfeit", "prohibited", "automatic increase"]
            medium_risk_keywords = ["must", "required", "responsible", "obligation", "mandatory"]
            
            if any(k in lower_p for k in high_risk_keywords):
                soft_risk = "high"
            elif any(k in lower_p for k in medium_risk_keywords):
                soft_risk = "medium"
            
            # Long clause heuristic
            if len(p.split()) > 60 and soft_risk == "low":
                soft_risk = "medium"
            
            clause = {
                "clause_id": cid,
                "original_text": p,
                "summary": p if len(p) < 200 else p[:197] + "...",
                "type": clause_type,
                "numeric_values": numeric_values,
                "soft_risk": soft_risk,
                "illegal": False,
                "illegal_reasons": []
            }
            clauses.append(clause)
            cid += 1
        
        # Overall summary
        total_clauses = len(clauses)
        summary = f"{total_clauses} clauses extracted and classified."
        
        result = {
            "text": input_text,
            "metadata": {"clauses_count": total_clauses},
            "clauses": clauses,
            "summary": summary
        }
        
        # Simulate latency
        time.sleep(0.2)
        return result
    
    def query(self, prompt: str) -> str:
        """Mock query for fallback"""
        return "I'm a mock adapter. Please use ClaudeLLMAdapter for real responses."
    
    def _classify_clause_type(self, text: str) -> str:
        """
        Classify clause type based on keywords.
        """
        text_lower = text.lower()
        
        if any(kw in text_lower for kw in ["security deposit", "bond", "deposit amount"]):
            return "bond"
        
        if any(kw in text_lower for kw in ["break lease", "early termination fee", "lease break"]):
            return "break_lease_fee"
        
        if any(kw in text_lower for kw in ["rent increase", "increase in rent", "rent will increase"]):
            return "rent_increase"
        
        if any(kw in text_lower for kw in ["monthly rent", "rent payment", "rent is due", "weekly rent"]):
            return "rent_payment"
        
        if any(kw in text_lower for kw in ["maintenance", "repairs", "repair obligations"]):
            return "maintenance"
        
        if any(kw in text_lower for kw in ["sublet", "subletting", "sub-let", "assign lease"]):
            return "subletting"
        
        if any(kw in text_lower for kw in ["utilities", "electricity", "water", "gas", "internet"]):
            return "utility_charges"
        
        if any(kw in text_lower for kw in ["early termination", "terminate early"]):
            return "early_termination"
        
        if any(kw in text_lower for kw in ["penalty", "fine", "charge for"]):
            return "penalty"
        
        return "other"


class ClaudeLLMAdapter(LLMAdapter):
    """
    Claude (Anthropic) LLM adapter for real conversational AI.
    """
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv("CLAUDE_API_KEY")
        if not self.api_key:
            raise ValueError("CLAUDE_API_KEY not found. Set it as environment variable or pass to constructor.")
        
        self.api_url = "https://api.anthropic.com/v1/messages"
        self.model_name = "claude-sonnet-4-20250514"
        
        # Keep MockLLMAdapter for document processing
        self.mock_adapter = MockLLMAdapter()
    
    def generate(self, prompt: str, *, input_text: str = "") -> Dict[str, Any]:
        """
        Use MockLLMAdapter's clause extraction for document processing.
        This keeps the structured extraction logic intact.
        """
        return self.mock_adapter.generate(prompt, input_text=input_text)
    
    def query(self, prompt: str) -> str:
        """
        Real conversational AI using Claude API.
        """
        try:
            headers = {
                "Content-Type": "application/json",
                "x-api-key": self.api_key,
                "anthropic-version": "2023-06-01"
            }
            
            data = {
                "model": self.model_name,
                "max_tokens": 2048,
                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            }
            
            response = requests.post(
                self.api_url,
                headers=headers,
                json=data,
                timeout=30
            )
            
            # Handle errors
            if response.status_code != 200:
                error_data = response.json() if response.text else {}
                error_msg = error_data.get('error', {}).get('message', f'HTTP {response.status_code}')
                return f"I apologize, but I encountered an error: {error_msg}"
            
            # Parse response
            result = response.json()
            
            # Extract text from content array
            content = result.get('content', [])
            if content and len(content) > 0:
                return content[0].get('text', 'No response generated')
            
            return "No response generated"
            
        except requests.exceptions.Timeout:
            return "Request timed out. Please try again."
        except requests.exceptions.RequestException as e:
            return f"Network error: {str(e)}"
        except json.JSONDecodeError:
            return "Failed to parse response. Please try again."
        except Exception as e:
            return f"I apologize, but I encountered an error: {str(e)}"


# For backward compatibility, keep GeminiLLMAdapter stub
class GeminiLLMAdapter(LLMAdapter):
    """
    DEPRECATED: Use ClaudeLLMAdapter instead.
    """
    def __init__(self, api_key: str = None):
        print("⚠️ WARNING: GeminiLLMAdapter is deprecated. Using ClaudeLLMAdapter instead.")
        self.claude_adapter = ClaudeLLMAdapter(api_key)
    
    def generate(self, prompt: str, *, input_text: str = "") -> Dict[str, Any]:
        return self.claude_adapter.generate(prompt, input_text=input_text)
    
    def query(self, prompt: str) -> str:
        return self.claude_adapter.query(prompt)