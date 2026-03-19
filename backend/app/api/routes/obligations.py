from datetime import datetime, timedelta

from fastapi import APIRouter, HTTPException, Query

from app.core.config import Settings
from app.core.models import AnalysisStatus
from app.services.database import get_analysis, list_contracts

router = APIRouter()


def _get_settings() -> Settings:
    return Settings()


@router.get("/")
async def list_obligations(
    contract_id: str | None = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
):
    """List obligations, optionally filtered by contract."""
    settings = _get_settings()

    if contract_id:
        analysis = await get_analysis(contract_id, settings)
        if analysis is None:
            raise HTTPException(status_code=404, detail="Analysis not found")

        obligations = [
            {"contract_id": contract_id, **o.model_dump(mode="json")}
            for o in analysis.obligations
        ]
        total = len(obligations)
        return {"obligations": obligations[skip : skip + limit], "total": total}

    # Collect obligations across all analyzed contracts
    all_obligations = []
    contracts, _ = await list_contracts(settings, skip=0, limit=500)

    for contract in contracts:
        analysis = await get_analysis(contract.id, settings)
        if analysis and analysis.status == AnalysisStatus.COMPLETED:
            for o in analysis.obligations:
                all_obligations.append(
                    {"contract_id": contract.id, "filename": contract.filename, **o.model_dump(mode="json")}
                )

    total = len(all_obligations)
    return {"obligations": all_obligations[skip : skip + limit], "total": total}


@router.get("/upcoming")
async def get_upcoming_obligations(days: int = Query(30, ge=1, le=365)):
    """Get obligations due within the next N days."""
    settings = _get_settings()
    now = datetime.utcnow()
    cutoff = now + timedelta(days=days)

    upcoming = []
    contracts, _ = await list_contracts(settings, skip=0, limit=500)

    for contract in contracts:
        analysis = await get_analysis(contract.id, settings)
        if analysis and analysis.status == AnalysisStatus.COMPLETED:
            for o in analysis.obligations:
                if o.due_date:
                    try:
                        due = datetime.fromisoformat(o.due_date)
                        if now <= due <= cutoff:
                            upcoming.append(
                                {
                                    "contract_id": contract.id,
                                    "filename": contract.filename,
                                    **o.model_dump(mode="json"),
                                }
                            )
                    except ValueError:
                        # Non-ISO date strings (e.g., "within 30 days of execution") — include them
                        upcoming.append(
                            {
                                "contract_id": contract.id,
                                "filename": contract.filename,
                                **o.model_dump(mode="json"),
                            }
                        )

    upcoming.sort(key=lambda x: x.get("due_date") or "9999")
    total = len(upcoming)
    return {"obligations": upcoming, "total": total}
