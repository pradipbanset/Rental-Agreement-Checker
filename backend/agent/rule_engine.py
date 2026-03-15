"""
agent_hybrid_engine.py

Single-file intelligent hybrid engine (law + fairness + LLM reasoning).

How it works (high level):
- Contains compact, auditable rule sets for Australian states (NSW + example VIC entries).
- Contains fairness rules (subjective but explicit patterns and heuristics).
- Uses regex/text checks and numeric checks.
- Integrates with an external LLM adapter if available (expects `llm_adapters.llm_query(prompt)` to return a string).
- Produces a structured assessment for each clause including: verdict, score, reasons, and optional LLM explanation.

Usage:
    from agent_hybrid_engine import evaluate_contract, SAMPLE_CLAUSES
    results = evaluate_contract(SAMPLE_CLAUSES, state="NSW")

This file is intentionally self-contained but modular enough to be split later.

"""

from typing import Dict, Any, List, Optional, Tuple
import re
import math
import json

# Try to import a user-provided LLM adapter. If not available, use a fallback stub.
try:
    import llm_adapters
    LLM_AVAILABLE = hasattr(llm_adapters, "llm_query")
except Exception:
    llm_adapters = None
    LLM_AVAILABLE = False


# Compact state rule sets

# NOTE: These are compact, focused examples — expand with official legal sources for production use.
STATE_RULES = {
    "NSW": {
        "bond": {"max_weeks": 4},
        "break_lease_fee": {"max_weeks": 4},
        "rent_increase": {"min_notice_days": 60, "max_frequency_months": 12},
        # Additional common rules
        "entry_notice_days": {"routine_inspection": 7},
        "eviction": {"minimum_notice_days": 90},
    },
    "VIC": {
        "bond": {"max_weeks": 4},
        "rent_increase": {"min_notice_days": 60, "max_frequency_months": 12},
        "entry_notice_days": {"routine_inspection": 24},  # hours in VIC example
        "eviction": {"minimum_notice_days": 60},
    },
}


# Fairness heuristics and patterns

# These are subjective heuristics intended to flag potentially unfair clauses.
FAIRNESS_PATTERNS = [
    # Pattern, reason, severity (1-10)
    (re.compile(r"unrestricted access", re.I), "Landlord claims unrestricted access to the property", 8),
    (re.compile(r"all repairs.*tenant", re.I), "Clause makes tenant responsible for all repairs, including structural", 9),
    (re.compile(r"no refund.*bond", re.I), "Bond declared non-refundable without cause", 8),
    (re.compile(r"terminate.*without notice|terminate at any time", re.I), "Landlord can terminate without notice", 10),
    (re.compile(r"tenant must pay.*legal fees", re.I), "Tenant required to pay landlord's legal fees", 7),
]

# Numeric thresholds for fairness (example heuristics)
FAIRNESS_THRESHOLDS = {
    "penalty_weeks_upper_bound": 2,  # penalties > 2 weeks are suspect
    "excessive_fee_ratio": 1.5,  # fees > 1.5x of reasonable estimate deemed excessive
}


# Helper utilities


def safe_lower(s: Optional[str]) -> str:
    return (s or "").lower()


def extract_numbers_from_text(text: str) -> Dict[str, float]:
    """Attempt to extract numbers like weeks, $, days, months from a clause text."""
    res = {}
    # dollars
    m = re.search(r"\$\s*([0-9,]+(?:\.[0-9]{1,2})?)", text)
    if m:
        res["amount"] = float(m.group(1).replace(',', ''))
    # weeks
    m = re.search(r"([0-9]+(?:\.[0-9]+)?)\s*weeks?", text, re.I)
    if m:
        res["weeks"] = float(m.group(1))
    # days
    m = re.search(r"([0-9]+)\s*days?", text, re.I)
    if m:
        res["days"] = int(m.group(1))
    # months
    m = re.search(r"([0-9]+)\s*months?", text, re.I)
    if m:
        res["months"] = int(m.group(1))
    return res



# LLM Reasoning wrapper


def llm_reasoning_prompt(clause: Dict[str, Any], state: str) -> str:
    """Create a prompt to ask the LLM for an explanation about legality and fairness."""
    t = clause.get("text", "").strip()
    prompt = (
        f"You are an expert in Australian residential tenancy law (state: {state}).\n"
        "Assess the following rental contract clause for legal compliance and fairness. "
        "Return a short JSON with keys: verdict (Legal/Illegal/Potentially Unfair/Needs Manual Review), "
        "explanation (one-paragraph), and recommended_action. Do not add any extra keys.\n\n"
        f"Clause text:\n" + t
    )
    return prompt


def call_llm_for_clause(clause: Dict[str, Any], state: str) -> Optional[Dict[str, Any]]:
    """Call configured LLM adapter to get an authoritative explanation. Returns parsed JSON or None."""
    if not LLM_AVAILABLE:
        return None
    prompt = llm_reasoning_prompt(clause, state)
    try:
        raw = llm_adapters.llm_query(prompt)
        # Try to find JSON in the response
        m = re.search(r"\{.*\}", raw, re.S)
        if m:
            j = json.loads(m.group(0))
            return j
        # If response itself is JSON
        try:
            return json.loads(raw)
        except Exception:
            # fallback: return as explanation only
            return {"verdict": "Needs Manual Review", "explanation": raw[:1000], "recommended_action": "Ask legal counsel"}
    except Exception as e:
        return {"verdict": "Needs Manual Review", "explanation": f"LLM call failed: {e}", "recommended_action": "Retry LLM or fallback"}



# Core evaluation logic


def assess_clause_legality_hybrid(clause: Dict[str, Any], state_rules: Dict[str, Any], state_code: str = "NSW") -> Dict[str, Any]:
    """Assess clause using deterministic rules + fairness heuristics + optional LLM reasoning.

    Returns a dict with:
      - verdict: 'Legal'|'Illegal'|'Potentially Unfair'|'Needs Manual Review'
      - score: 0-100 (higher = more compliant/safe)
      - illegal (bool)
      - reasons (list)
      - llm_explanation (optional)
    """
    reasons: List[str] = []
    illegal = False
    score = 100.0

    ctype = clause.get("type", "unknown")
    nums = clause.get("numeric_values", {})
    text = clause.get("text", "")

    # If numbers missing try to extract from text
    if not nums:
        extracted = extract_numbers_from_text(text)
        if extracted:
            nums = extracted
            clause["numeric_values"] = nums

    # Deterministic numeric checks (expandable)

    if ctype == "bond":
        bond_rules = state_rules.get("bond", {})
        max_weeks = bond_rules.get("max_weeks", 4)
        if "weeks" in nums:
            if nums["weeks"] > max_weeks:
                illegal = True
                reasons.append(f"Bond of {nums['weeks']} weeks exceeds {state_code} maximum of {max_weeks} weeks")
                score -= 40
        elif "amount" in nums and clause.get("weekly_rent"):
            weekly_rent = clause["weekly_rent"]
            max_amount = weekly_rent * max_weeks
            if nums["amount"] > max_amount:
                illegal = True
                reasons.append(f"Bond amount ${nums['amount']:.2f} exceeds maximum of ${max_amount:.2f} ({max_weeks} weeks × ${weekly_rent:.2f})")
                score -= 40
        elif "amount" in nums and "weekly_rent" not in clause:
            reasons.append("Bond amount present but weekly_rent not provided — cannot fully validate")
            score -= 5

    # Break lease fee 
    if ctype == "break_lease_fee":
        fee_rules = state_rules.get("break_lease_fee", {})
        max_weeks = fee_rules.get("max_weeks", 4)
        if "weeks" in nums and nums["weeks"] > max_weeks:
            illegal = True
            reasons.append(f"Break-lease fee of {nums['weeks']} weeks exceeds {state_code} maximum of {max_weeks} weeks")
            score -= 35
        if "amount" in nums and "weekly_rent" in clause:
            weekly_rent = clause["weekly_rent"]
            max_amount = weekly_rent * max_weeks
            if nums["amount"] > max_amount:
                illegal = True
                reasons.append(f"Break-lease fee ${nums['amount']:.2f} exceeds maximum of ${max_amount:.2f} ({max_weeks} weeks × ${weekly_rent:.2f})")
                score -= 35

    # Rent increase 
    if ctype == "rent_increase":
        inc_rules = state_rules.get("rent_increase", {})
        min_notice = inc_rules.get("min_notice_days", 60)
        max_freq = inc_rules.get("max_frequency_months", 12)
        if "days" in nums and nums["days"] < min_notice:
            illegal = True
            reasons.append(f"Rent increase notice period of {nums['days']} days is less than {state_code} minimum of {min_notice} days")
            score -= 30
        if "months" in nums and nums["months"] < max_freq:
            illegal = True
            reasons.append(f"Rent increases cannot occur more frequently than every {max_freq} months (clause mentions {nums['months']} months)")
            score -= 30

    # Entry / inspections 
    if ctype == "entry" or "entry" in safe_lower(text):
        entry_rules = state_rules.get("entry_notice_days", {})
        # We look for days in text
        if "days" in nums:
            # routine_inspection might be in hours or days; use a simple heuristic
            allowed = entry_rules.get("routine_inspection")
            if allowed and nums["days"] < allowed:
                reasons.append(f"Entry notice of {nums['days']} days is shorter than {state_code} allowed routine inspection notice ({allowed})")
                score -= 10


    # Fairness heuristics

    # Pattern-based flags
    for pattern, reason_text, severity in FAIRNESS_PATTERNS:
        if pattern.search(text):
            reasons.append(f"Potentially unfair: {reason_text}")
            score -= severity * 2

    # Numeric fairness heuristics (penalties)
    if ctype == "penalty":
        if "weeks" in nums and nums["weeks"] > FAIRNESS_THRESHOLDS["penalty_weeks_upper_bound"]:
            reasons.append(f"Penalty of {nums['weeks']} weeks is likely excessive")
            score -= 20

    # If clause contains absolute absolutes
    if re.search(r"\b(no refund|no liability|at any time|without notice)\b", text, re.I):
        reasons.append("Clause uses absolute language that often indicates unfair or illegal terms")
        score -= 15

    
    # LLM reasoning: use for nuanced textual legal interpretation
    
    llm_explanation = None
    if LLM_AVAILABLE:
        llm_out = call_llm_for_clause(clause, state_code)
        if llm_out:
            # If LLM returns explicit verdict, integrate it
            llm_explanation = llm_out
            v = safe_lower(llm_out.get("verdict", ""))
            if "illegal" in v:
                illegal = True
                reasons.append("LLM flagged as illegal: " + llm_out.get("explanation", ""))
                score -= 30
            elif "potentially unfair" in v or "unfair" in v:
                reasons.append("LLM flagged as potentially unfair: " + llm_out.get("explanation", ""))
                score -= 20
            elif "needs manual" in v or "manual" in v:
                reasons.append("LLM recommends manual review: " + llm_out.get("explanation", ""))
                score -= 10

    # Final adjustments
    score = max(0.0, min(100.0, score))

    # Decide final verdict
    if illegal:
        verdict = "Illegal"
    else:
        # if many reasons or low score, mark potentially unfair
        if score < 60 or any("Potentially unfair" in r for r in reasons):
            verdict = "Potentially Unfair"
        elif score < 80 and reasons:
            verdict = "Needs Manual Review"
        else:
            verdict = "Legal"

    return {
        "verdict": verdict,
        "score": round(score, 1),
        "illegal": illegal,
        "reasons": reasons,
        "llm_explanation": llm_explanation,
        "clause": clause,
    }



# Contract-level evaluation


def evaluate_contract(clauses: List[Dict[str, Any]], state: str = "NSW") -> Dict[str, Any]:
    """Evaluate a list of clauses and return an overall report."""
    state_rules = STATE_RULES.get(state.upper(), {})
    results = [assess_clause_legality_hybrid(c, state_rules, state.upper()) for c in clauses]

    # Simple aggregation
    scores = [r["score"] for r in results]
    avg_score = sum(scores) / len(scores) if scores else 100

    illegal_count = sum(1 for r in results if r["illegal"]) 
    potentially_unfair = sum(1 for r in results if r["verdict"] == "Potentially Unfair")

    overall_verdict = "Legal"
    if illegal_count > 0:
        overall_verdict = "Contains Illegal Clauses"
    elif potentially_unfair > 0 or avg_score < 70:
        overall_verdict = "Potentially Unfair — Review Recommended"

    return {
        "state": state,
        "overall_verdict": overall_verdict,
        "average_score": round(avg_score, 1),
        "illegal_count": illegal_count,
        "clauses_evaluated": len(results),
        "results": results,
    }



# Example usage (SAMPLE_CLAUSES)

SAMPLE_CLAUSES = [
    {
        "type": "bond",
        "text": "Tenant must pay bond of 6 weeks' rent.",
        "numeric_values": {"weeks": 6},
        "weekly_rent": 500.0,
    },
    {
        "type": "rent_increase",
        "text": "Landlord may increase rent every 6 months with 30 days' notice.",
        "numeric_values": {"months": 6, "days": 30},
    },
    {
        "type": "penalty",
        "text": "If tenant breaks lease, tenant pays 8 weeks of rent as penalty.",
        "numeric_values": {"weeks": 8},
    },
    {
        "type": "entry",
        "text": "Landlord may enter the property for inspections at any time without notice.",
    }
]



if __name__ == "__main__":
    report = evaluate_contract(SAMPLE_CLAUSES, state="NSW")
    print(json.dumps(report, indent=2))
