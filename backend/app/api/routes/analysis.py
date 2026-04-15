import uuid
import logging
import traceback
from datetime import datetime

from fastapi import APIRouter, BackgroundTasks, HTTPException

from app.core.config import Settings
from app.core.models import AnalysisResult, AnalysisStatus
from app.services.document_parser import parse_document
from app.services.database import (
    get_contract,
    get_analysis,
    save_analysis,
    update_analysis_status,
    get_dashboard_stats,
)
from app.agents.pipeline import run_analysis_pipeline

logger = logging.getLogger(__name__)
router = APIRouter()


def _get_settings() -> Settings:
    return Settings()


async def _run_analysis_background(contract_id: str, analysis_id: str, settings: Settings):
    """Background task that runs the full analysis pipeline."""
    try:
        logger.info(f"Starting analysis for contract {contract_id} (analysis_id={analysis_id})")
        await update_analysis_status(contract_id, AnalysisStatus.IN_PROGRESS, settings)

        contract = await get_contract(contract_id, settings)
        if contract is None:
            logger.error(f"Contract {contract_id} not found")
            await update_analysis_status(
                contract_id, AnalysisStatus.FAILED, settings,
                error_message="Contract not found",
            )
            return

        logger.info(f"Parsing document: {contract.file_path}")
        contract_text = await parse_document(contract.file_path, settings)
        logger.info(f"Document parsed, {len(contract_text)} characters. Running AI pipeline...")
        
        result = await run_analysis_pipeline(contract_text, contract_id, analysis_id, settings)
        logger.info(f"Analysis complete for {contract_id}: {len(result.risk_flags)} risks, {len(result.obligations)} obligations")
        await save_analysis(result, settings)

    except Exception as e:
        error_msg = f"{type(e).__name__}: {str(e)}"
        logger.error(f"Analysis failed for {contract_id}: {error_msg}")
        logger.error(traceback.format_exc())
        await update_analysis_status(
            contract_id, AnalysisStatus.FAILED, settings,
            error_message=error_msg,
        )


@router.get("/dashboard/stats")
async def get_dashboard_stats_endpoint():
    """Get aggregated dashboard statistics."""
    settings = _get_settings()
    stats = await get_dashboard_stats(settings)
    return stats


@router.post("/{contract_id}")
async def trigger_analysis(contract_id: str, background_tasks: BackgroundTasks):
    """Trigger AI analysis pipeline for a contract. Runs in background."""
    settings = _get_settings()

    contract = await get_contract(contract_id, settings)
    if contract is None:
        raise HTTPException(status_code=404, detail="Contract not found")

    # Create a pending analysis record with a fixed ID
    analysis_id = uuid.uuid4().hex
    analysis = AnalysisResult(
        id=analysis_id,
        contract_id=contract_id,
        status=AnalysisStatus.PENDING,
        created_at=datetime.utcnow(),
    )
    await save_analysis(analysis, settings)

    # Pass analysis_id so the pipeline updates the same record
    background_tasks.add_task(_run_analysis_background, contract_id, analysis_id, settings)

    return {"contract_id": contract_id, "status": "pending"}


@router.get("/{contract_id}")
async def get_analysis_endpoint(contract_id: str):
    """Get analysis results for a contract."""
    settings = _get_settings()
    analysis = await get_analysis(contract_id, settings)
    if analysis is None:
        raise HTTPException(status_code=404, detail="Analysis not found")

    return analysis.model_dump(mode="json")


@router.get("/{contract_id}/status")
async def get_analysis_status(contract_id: str):
    """Poll analysis status for a contract."""
    settings = _get_settings()
    analysis = await get_analysis(contract_id, settings)
    if analysis is None:
        raise HTTPException(status_code=404, detail="Analysis not found")

    return {
        "contract_id": contract_id,
        "status": analysis.status.value,
        "error_message": analysis.error_message,
    }
