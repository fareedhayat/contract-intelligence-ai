import uuid
from datetime import datetime
from pathlib import Path

from fastapi import APIRouter, HTTPException, Query

from app.core.config import Settings
from app.core.models import ContractDocument, AnalysisStatus
from app.services import cuad_loader
from app.services.database import save_contract

router = APIRouter()


def _get_settings() -> Settings:
    return Settings()


@router.get("/contracts")
async def list_cuad_contracts(
    contract_type: str | None = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=500),
):
    """List available CUAD dataset PDF contracts, optionally filtered by type."""
    settings = _get_settings()
    data_path = settings.cuad_data_path

    try:
        if contract_type:
            filenames = cuad_loader.filter_pdf_by_type(contract_type, data_path)
        else:
            filenames = cuad_loader.list_pdf_contracts(data_path)
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))

    total = len(filenames)
    page = filenames[skip : skip + limit]

    return {"contracts": page, "total": total}


@router.get("/contract-types")
async def list_cuad_contract_types():
    """List all contract types available in the CUAD dataset."""
    settings = _get_settings()
    try:
        types = cuad_loader.get_contract_types(settings.cuad_data_path)
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))

    return {"types": types}


@router.post("/import/{filename}")
async def import_cuad_contract(filename: str):
    """Import a single CUAD PDF contract into the system."""
    settings = _get_settings()

    try:
        pdf_path = cuad_loader.get_contract_pdf_path(filename, settings.cuad_data_path)
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))

    pdf_filename = Path(pdf_path).name
    file_size = Path(pdf_path).stat().st_size

    contract = ContractDocument(
        id=uuid.uuid4().hex,
        filename=pdf_filename,
        upload_date=datetime.utcnow(),
        file_path=pdf_path,
        status=AnalysisStatus.PENDING,
    )

    await save_contract(contract, settings)

    return {"contract_id": contract.id, "filename": pdf_filename, "file_size_bytes": file_size}


@router.post("/import-batch")
async def import_cuad_batch(
    contract_type: str | None = Query(None),
    limit: int = Query(10, ge=1, le=50),
):
    """Import a batch of CUAD PDF contracts by type."""
    settings = _get_settings()
    data_path = settings.cuad_data_path

    try:
        if contract_type:
            filenames = cuad_loader.filter_pdf_by_type(contract_type, data_path)
        else:
            filenames = cuad_loader.list_pdf_contracts(data_path)
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))

    filenames = filenames[:limit]
    imported = []

    for filename in filenames:
        pdf_path = cuad_loader.get_contract_pdf_path(filename, data_path)
        pdf_filename = Path(pdf_path).name
        contract = ContractDocument(
            id=uuid.uuid4().hex,
            filename=pdf_filename,
            upload_date=datetime.utcnow(),
            file_path=pdf_path,
            status=AnalysisStatus.PENDING,
        )
        await save_contract(contract, settings)
        imported.append({"contract_id": contract.id, "filename": pdf_filename})

    return {"imported": len(imported), "contracts": imported}
