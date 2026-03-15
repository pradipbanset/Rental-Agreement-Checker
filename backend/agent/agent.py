from typing import Dict, Any

from .llm_adapters import LLMAdapter, MockLLMAdapter
from .prompts import EXTRACTION_PROMPT

from .rule_engine import (
    assess_clause_legality_hybrid,
    evaluate_contract,
    SAMPLE_CLAUSES,
    STATE_RULES
)


class MainAgent:
    """
    Main AI Agent that performs:
      - LLM clause extraction
      - Hybrid legality & fairness reasoning
      - Human-readable report generation
    """

    def __init__(self, llm: LLMAdapter = None, default_state: str = "NSW"):
        self.llm = llm or MockLLMAdapter()
        self.state = default_state

    def extract_and_classify(self, raw_text: str) -> Dict[str, Any]:
        """
        1. Extract clauses using LLM
        2. Run hybrid (rule-based + LLM fairness) legality analysis
        3. Produce structured + human-readable report
        """
        extraction = self.llm.generate(EXTRACTION_PROMPT, input_text=raw_text)

        clauses = extraction.get("clauses", [])
        metadata = extraction.get("metadata", {})

        # Get the rule-set for the chosen state
        rules = STATE_RULES.get(self.state, {})


        # Run hybrid analysis for each clause
        for clause in clauses:
            assess_clause_legality_hybrid(
                clause,
                rules,
                state_code=self.state 
            )

        # Build final report
        report = {
            "text": extraction.get("text", raw_text),
            "metadata": metadata,
            "clauses": clauses,
            "summary": self.generate_human_readable_report(clauses)
        }
        return report

    def generate_human_readable_report(self, clauses):
        """
        Convert structured clause results into a readable summary.
        """
        if not clauses:
            return "No clauses detected in the contract."

        illegal = [c for c in clauses if c.get("illegal")]
        high_risk = [c for c in clauses if c.get("risk_level") == "high"]
        medium_risk = [c for c in clauses if c.get("risk_level") == "medium"]

        summary = []

        summary.append("Contract Review Report:")

        # If safe
        if not illegal and not high_risk and not medium_risk:
            summary.append(
                "This contract appears generally fair with no illegal, high-risk, or questionable clauses."
            )

        #  Illegal clauses
        if illegal:
            summary.append("Illegal or prohibited clauses found:")
            for c in illegal:
                summary.append(
                    f"- Clause {c['clause_id']} is ILLEGAL: {c['original_text']} "
                    f"(Reason: {', '.join(c.get('illegal_reasons', []))})"
                )

        # High-risk fairness
        if high_risk:
            summary.append("High-risk clauses (may be unfair or imbalanced):")
            for c in high_risk:
                summary.append(
                    f"- Clause {c['clause_id']}: {c['original_text']} "
                    f"(LLM fairness score: {c.get('fairness_score')})"
                )

        # Medium risk
        if medium_risk:
            summary.append("Medium-risk clauses (needs review):")
            for c in medium_risk:
                summary.append(
                    f"- Clause {c['clause_id']}: {c['original_text']}"
                )

        # Numeric values summary
        numeric_clauses = [c for c in clauses if c.get("numeric_values")]
        if numeric_clauses:
            summary.append("Detected numeric values:")
            for c in numeric_clauses:
                summary.append(
                    f"- Clause {c['clause_id']}: {c['numeric_values']}"
                )

        return "\n".join(summary)
