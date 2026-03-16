from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()


class CompareRequest(BaseModel):
    contract_a_id: str
    contract_b_id: str


@router.post("/")
async def compare_contracts(request: CompareRequest):
    """Compare two contracts side-by-side using AI."""
    # TODO: Phase 4 — run_comparison()
    return {"message": "not implemented"}


@router.get("/{comparison_id}")
async def get_comparison(comparison_id: str):
    """Get a previously computed comparison result."""
    # TODO: Phase 2 — get from Cosmos DB
    return {"message": "not implemented"}
