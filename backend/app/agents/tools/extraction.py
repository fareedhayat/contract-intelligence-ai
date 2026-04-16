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
