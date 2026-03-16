from fastapi import APIRouter, Query

router = APIRouter()


@router.get("/")
async def list_obligations(
    contract_id: str | None = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
):
    """List obligations, optionally filtered by contract."""
    # TODO: Phase 2 — query obligations from Cosmos DB
    return {"obligations": [], "total": 0}


@router.get("/upcoming")
async def get_upcoming_obligations(days: int = Query(30, ge=1, le=365)):
    """Get obligations due within the next N days."""
    # TODO: Phase 2 — query by due_date
    return {"obligations": [], "total": 0}
