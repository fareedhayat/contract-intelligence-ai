from typing import Annotated

from agent_framework import tool
from pydantic import Field

from app.core.config import Settings
from app.services.cuad_loader import get_ground_truth


@tool
def lookup_cuad_ground_truth(
    filename: Annotated[str, Field(description="CUAD contract filename (e.g., 'ContractName.txt')")],
    clause_type: Annotated[str, Field(description="Clause category name from CUAD's 41 categories")],
) -> str:
    """Look up CUAD expert annotations for a specific contract and clause type.
    Returns the ground truth answer spans, or 'No annotation found' if empty."""
    settings = Settings()
    try:
        ground_truth = get_ground_truth(filename, settings.cuad_data_path)
    except (FileNotFoundError, ValueError) as e:
        return f"Error: {e}"

    annotations = ground_truth.get(clause_type, [])
    if not annotations:
        return "No annotation found for this clause type."
    return "; ".join(annotations)


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
            # Check for very short cure periods
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


@tool
def parse_contract_dates(
    text: Annotated[str, Field(description="Text containing dates to extract and normalize")],
) -> str:
    """Extract and normalize dates found in contract text.
    Returns a list of identified dates with context."""
    import re

    date_patterns = [
        (r'\b(\d{1,2}[/\-]\d{1,2}[/\-]\d{2,4})\b', "numeric date"),
        (r'\b(January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},?\s+\d{4}\b', "full date"),
        (r'\b(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\.?\s+\d{1,2},?\s+\d{4}\b', "abbreviated date"),
        (r'\b\d{4}[/\-]\d{1,2}[/\-]\d{1,2}\b', "ISO date"),
    ]

    found_dates = []
    for pattern, label in date_patterns:
        matches = re.finditer(pattern, text, re.IGNORECASE)
        for match in matches:
            # Get surrounding context (up to 50 chars before and after)
            start = max(0, match.start() - 50)
            end = min(len(text), match.end() + 50)
            context = text[start:end].replace("\n", " ").strip()
            found_dates.append(f"{match.group()} ({label}) — ...{context}...")

    if not found_dates:
        return "No dates found in the provided text."
    return "\n".join(found_dates)
