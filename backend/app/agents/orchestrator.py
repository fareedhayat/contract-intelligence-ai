from datetime import datetime

from app.core.config import Settings
from app.core.models import AnalysisResult, AnalysisStatus, ComparisonResult
from app.agents.extractor_agent import run_extractor
from app.agents.risk_agent import run_risk_analyst, RiskResponse
from app.agents.obligation_agent import run_obligation_tracker, ObligationResponse
from app.agents.summary_agent import run_summarizer
from app.agents.comparison_agent import run_comparison as _run_comparison


async def run_analysis_pipeline(
    contract_text: str,
    contract_id: str,
    analysis_id: str,
    settings: Settings,
) -> AnalysisResult:
    """Run the 4-agent sequential analysis pipeline on a contract.

    Pipeline: DataExtractor → RiskAnalyst → ObligationTracker → Summarizer
    Each agent receives the original contract text plus prior agents' output.
    """
    # Agent 1: Extract structured data
    extracted_data = await run_extractor(contract_text, settings)

    # Agent 2: Analyze risks (receives extraction context)
    risk_flags = await run_risk_analyst(
        contract_text,
        extracted_data.model_dump_json(),
        settings,
    )

    # Agent 3: Extract obligations (receives extraction context)
    obligations = await run_obligation_tracker(
        contract_text,
        extracted_data.model_dump_json(),
        settings,
    )

    # Agent 4: Summarize (receives all prior context)
    prior_context = (
        f"Extracted data:\n{extracted_data.model_dump_json()}\n\n"
        f"Risk flags:\n{RiskResponse(risk_flags=risk_flags).model_dump_json()}\n\n"
        f"Obligations:\n{ObligationResponse(obligations=obligations).model_dump_json()}"
    )
    summary = await run_summarizer(contract_text, prior_context, settings)

    return AnalysisResult(
        id=analysis_id,
        contract_id=contract_id,
        status=AnalysisStatus.COMPLETED,
        extracted_data=extracted_data,
        risk_flags=risk_flags,
        obligations=obligations,
        summary=summary,
        created_at=datetime.utcnow(),
        completed_at=datetime.utcnow(),
    )


async def run_comparison(
    analysis_a: AnalysisResult,
    analysis_b: AnalysisResult,
    settings: Settings,
) -> ComparisonResult:
    """Compare two contract analyses side by side."""
    return await _run_comparison(analysis_a, analysis_b, settings)
