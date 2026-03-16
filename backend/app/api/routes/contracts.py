from fastapi import APIRouter, UploadFile, File, Query

router = APIRouter()


@router.post("/upload")
async def upload_contract(file: UploadFile = File(...)):
    """Upload a contract document for analysis."""
    # TODO: Phase 2 — save_file() + save_contract()
    return {"message": "not implemented"}


@router.get("/")
async def list_contracts(skip: int = Query(0, ge=0), limit: int = Query(20, ge=1, le=100)):
    """List all uploaded contracts with pagination."""
    # TODO: Phase 2 — list_contracts()
    return {"contracts": [], "total": 0}


@router.get("/{contract_id}")
async def get_contract(contract_id: str):
    """Get a specific contract by ID."""
    # TODO: Phase 2 — get_contract()
    return {"message": "not implemented"}


@router.delete("/{contract_id}")
async def delete_contract(contract_id: str):
    """Delete a contract and its analysis results."""
    # TODO: Phase 2 — delete_contract()
    return {"message": "not implemented"}
