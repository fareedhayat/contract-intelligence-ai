import uuid
from datetime import datetime

from fastapi import APIRouter, HTTPException, UploadFile, File, Query

from app.core.config import Settings
from app.core.models import ContractDocument, AnalysisStatus
from app.services.storage import save_file
from app.services.document_parser import parse_document
from app.services.database import (
    save_contract,
    get_contract,
    list_contracts,
    delete_contract,
    delete_all_data,
)

router = APIRouter()


def _get_settings() -> Settings:
    return Settings()


@router.post("/upload")
async def upload_contract_endpoint(file: UploadFile = File(...)):
    """Upload a contract document for analysis."""
    settings = _get_settings()

    file_bytes = await file.read()
    file_path = await save_file(file_bytes, file.filename, settings)

    contract = ContractDocument(
        id=uuid.uuid4().hex,
        filename=file.filename,
        upload_date=datetime.utcnow(),
        file_path=file_path,
        status=AnalysisStatus.PENDING,
    )
    await save_contract(contract, settings)

    return {"contract_id": contract.id, "filename": contract.filename}


@router.get("/")
async def list_contracts_endpoint(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
):
    """List all uploaded contracts with pagination."""
    settings = _get_settings()
    contracts, total = await list_contracts(settings, skip=skip, limit=limit)

    return {
        "contracts": [c.model_dump(mode="json") for c in contracts],
        "total": total,
    }


@router.get("/{contract_id}")
async def get_contract_endpoint(contract_id: str):
    """Get a specific contract by ID."""
    settings = _get_settings()
    contract = await get_contract(contract_id, settings)
    if contract is None:
        raise HTTPException(status_code=404, detail="Contract not found")

    return contract.model_dump(mode="json")


@router.delete("/{contract_id}")
async def delete_contract_endpoint(contract_id: str):
    """Delete a contract and its analysis results."""
    settings = _get_settings()
    contract = await get_contract(contract_id, settings)
    if contract is None:
        raise HTTPException(status_code=404, detail="Contract not found")

    await delete_contract(contract_id, settings)
    return {"deleted": contract_id}


@router.delete("/cleanup/all")
async def delete_all_data_endpoint():
    """Delete ALL contracts, analyses, and comparisons. Fresh start."""
    settings = _get_settings()
    result = await delete_all_data(settings)
    return result
