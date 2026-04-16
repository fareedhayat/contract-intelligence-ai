from typing import Annotated

from agent_framework import tool
from pydantic import Field


@tool
def check_risk_rules(
    clause_text: Annotated[str, Field(description="The contract clause text to evaluate")],
    clause_type: Annotated[str, Field(description="Type of clause (e.g., 'liability', 'termination', 'indemnification')")],
) -> str:
    """Check a clause against known risk rules and thresholds.
    Returns risk indicators based on common contract risk patterns."""
    clause_lower = clause_text.lower()
    risks = []

    if clause_type == "liability":
        if any(phrase in clause_lower for phrase in ["unlimited liability", "uncapped", "no limitation"]):
            risks.append("HIGH: Uncapped liability detected — no limit on potential damages.")
        if "consequential damages" in clause_lower and "exclude" not in clause_lower:
            risks.append("HIGH: Consequential damages not excluded.")
        if "cap" in clause_lower and any(w in clause_lower for w in ["contract value", "fees paid"]):
            risks.append("LOW: Liability capped at contract value — standard provision.")

    elif clause_type == "termination":
        if "for convenience" in clause_lower and "either party" not in clause_lower:
            risks.append("MEDIUM: One-sided termination for convenience.")
        if "without cause" in clause_lower:
            risks.append("MEDIUM: Termination without cause permitted.")
        if any(phrase in clause_lower for phrase in ["cure period", "notice"]):
            for days in ["5 days", "7 days", "5 business days"]:
                if days in clause_lower:
                    risks.append(f"MEDIUM: Short cure period ({days}).")

    elif clause_type == "indemnification":
        if any(phrase in clause_lower for phrase in ["unlimited indemnification", "uncapped indemnification"]):
            risks.append("HIGH: Uncapped indemnification obligation.")
        if "hold harmless" in clause_lower and "mutual" not in clause_lower:
            risks.append("MEDIUM: One-sided hold harmless clause.")

    elif clause_type == "intellectual_property":
        if any(phrase in clause_lower for phrase in ["assigns all", "full ownership", "work for hire"]):
            risks.append("HIGH: Full IP assignment to one party.")
        if "perpetual" in clause_lower and "license" in clause_lower:
            risks.append("MEDIUM: Perpetual license grant.")

    elif clause_type == "exclusivity":
        if any(phrase in clause_lower for phrase in ["exclusive", "sole and exclusive"]):
            risks.append("MEDIUM: Exclusive dealing arrangement.")

    elif clause_type == "competition":
        if "non-compete" in clause_lower or "non compete" in clause_lower:
            risks.append("MEDIUM: Non-compete restriction present.")
            for period in ["3 year", "4 year", "5 year"]:
                if period in clause_lower:
                    risks.append(f"HIGH: Extended non-compete period ({period}s).")

    if not risks:
        return "No specific risk patterns detected for this clause."
    return "\n".join(risks)
