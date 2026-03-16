from fastapi import APIRouter, Query

router = APIRouter()


@router.get("/contracts")
async def list_cuad_contracts(
    contract_type: str | None = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=500),
):
    """List available CUAD dataset contracts."""
    # TODO: Phase 3 — list_contracts() / filter_by_type()
    return {"contracts": [], "total": 0}


@router.post("/import/{filename}")
async def import_cuad_contract(filename: str):
    """Import a single CUAD contract into the system."""
    # TODO: Phase 3 — get_contract_text() + save_contract()
    return {"message": "not implemented"}


@router.post("/import-batch")
async def import_cuad_batch(
    contract_type: str | None = Query(None),
    limit: int = Query(10, ge=1, le=50),
):
    """Import a batch of CUAD contracts by type."""
    # TODO: Phase 3 — batch import
    return {"message": "not implemented"}
