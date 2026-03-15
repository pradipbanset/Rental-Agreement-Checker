EXTRACTION_PROMPT = """
You are an advanced OCR + legal document extraction engine.

INPUT: raw text extracted from a rental contract (or full text of PDF).
TASK:
1) Split the contract into clauses. A clause is any numbered item, or paragraph that expresses a distinct obligation or right.
2) For each clause produce:
   - clause_id (incremental integer)
   - original_text
   - summary (1-2 sentences in plain English)
   - type (one of: rent_payment, bond, break_lease_fee, rent_increase, maintenance, subletting, utility_charges, early_termination, penalty, other)
   - numeric_values (if any): e.g. {"weeks": 8, "amount": 1200}
Return the result as JSON with keys "text", "metadata" (empty if unknown), and "clauses" list.
Return ONLY JSON.

If you are given raw images or PDF content, first extract text; but above input will be the text string.
"""

CLASSIFY_PROMPT = """
You are a legal classifier for Australian residential tenancies.
Given a clause JSON object as:
{{
  "clause_id": {id},
  "original_text": "{text}"
}}
Return a JSON object with these fields:
- clause_id
- type (one of the types listed earlier)
- summary
- extracted_numbers (e.g., weeks or dollar amounts)
- soft_risk (low/medium/high) — your assessment whether the clause looks unusually harsh
Return only the JSON object.
"""
