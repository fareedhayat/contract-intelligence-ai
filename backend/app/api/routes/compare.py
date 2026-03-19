from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.core.config import Settings
from app.services.database import get_analysis, save_comparison, get_comparison
from app.agents.pipeline import run_comparison

router = APIRouter()


def _get_settings() -> Settings:
    return Settings()


class CompareRequest(BaseModel):
    contract_a_id: str
    contract_b_id: str


@router.post("/")
async def compare_contracts(request: CompareRequest):
    """Compare two contracts side-by-side using AI."""
    settings = _get_settings()

    analysis_a = await get_analysis(request.contract_a_id, settings)
    if analysis_a is None:
        raise HTTPException(
            status_code=404,
            detail=f"Analysis not found for contract {request.contract_a_id}",
        )

    analysis_b = await get_analysis(request.contract_b_id, settings)
    if analysis_b is None:
        raise HTTPException(
            status_code=404,
            detail=f"Analysis not found for contract {request.contract_b_id}",
        )

    result = await run_comparison(analysis_a, analysis_b, settings)
    await save_comparison(result, settings)

    return result.model_dump(mode="json")


@router.get("/{comparison_id}")
async def get_comparison_endpoint(comparison_id: str):
    """Get a previously computed comparison result."""
    settings = _get_settings()
    comparison = await get_comparison(comparison_id, settings)
    if comparison is None:
        raise HTTPException(status_code=404, detail="Comparison not found")

    return comparison.model_dump(mode="json")
