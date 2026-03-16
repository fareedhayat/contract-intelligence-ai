from fastapi import APIRouter, BackgroundTasks

router = APIRouter()


@router.post("/{contract_id}")
async def trigger_analysis(contract_id: str, background_tasks: BackgroundTasks):
    """Trigger AI analysis pipeline for a contract. Runs in background."""
    # TODO: Phase 4 — run_analysis_pipeline() via background task
    return {"message": "not implemented"}


@router.get("/{contract_id}")
async def get_analysis(contract_id: str):
    """Get analysis results for a contract."""
    # TODO: Phase 2 — get_analysis()
    return {"message": "not implemented"}


@router.get("/{contract_id}/status")
async def get_analysis_status(contract_id: str):
    """Poll analysis status for a contract."""
    # TODO: Phase 2 — get_analysis() → status field
    return {"message": "not implemented"}


@router.get("/dashboard/stats")
async def get_dashboard_stats():
    """Get aggregated dashboard statistics."""
    # TODO: Phase 2 — get_dashboard_stats()
    return {"message": "not implemented"}
