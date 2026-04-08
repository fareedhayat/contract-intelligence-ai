import uuid
from datetime import datetime

from agent_framework import Agent
from agent_framework.openai import OpenAIChatCompletionClient

from app.core.config import Settings
from app.core.models import (
    AnalysisResult,
    AnalysisStatus,
    ComparisonResult,
    ContractSummary,
    ExtractedData,
    Obligation,
    RiskFlag,
    TermComparison,
)
from app.agents.prompts import (
    EXTRACTOR_PROMPT,
    RISK_PROMPT,
    OBLIGATION_PROMPT,
    SUMMARY_PROMPT,
    COMPARISON_PROMPT,
)
from app.agents.tools import (
    lookup_cuad_ground_truth,
    check_risk_rules,
    parse_contract_dates,
)


# --- Response models for structured output ---

from pydantic import BaseModel, Field


class ExtractorResponse(BaseModel):
    """Structured output from the DataExtractor agent."""
    extracted_data: ExtractedData


class RiskResponse(BaseModel):
    """Structured output from the RiskAnalyst agent."""
    risk_flags: list[RiskFlag] = Field(default_factory=list)


class ObligationResponse(BaseModel):
    """Structured output from the ObligationTracker agent."""
    obligations: list[Obligation] = Field(default_factory=list)


class SummaryResponse(BaseModel):
    """Structured output from the Summarizer agent."""
    summary: ContractSummary


class ComparisonResponse(BaseModel):
    """Structured output from the Comparison agent."""
    term_comparisons: list[TermComparison] = Field(default_factory=list)
    risk_diff: str = ""
    overall_assessment: str = ""


# --- Client factory ---

def create_client(settings: Settings) -> OpenAIChatCompletionClient:
    """Create an Azure OpenAI chat client using API key authentication."""
    return OpenAIChatCompletionClient(
        model=settings.azure_openai_deployment,
        azure_endpoint=settings.azure_openai_endpoint,
        api_version=settings.azure_openai_api_version,
        api_key=settings.azure_openai_api_key,
    )


# --- Analysis pipeline ---

async def run_analysis_pipeline(
    contract_text: str,
    contract_id: str,
    settings: Settings,
) -> AnalysisResult:
    """Run the 4-agent sequential analysis pipeline on a contract.

    Pipeline: DataExtractor → RiskAnalyst → ObligationTracker → Summarizer
    Each agent receives the original contract text plus prior agents' output.
    """
    client = create_client(settings)

    # Create agents using the stable Agent class
    extractor = Agent(
        client=client,
        name="DataExtractor",
        instructions=EXTRACTOR_PROMPT + "\n\nRespond with valid JSON matching this schema: " + ExtractorResponse.model_json_schema().__str__(),
        tools=[parse_contract_dates],
    )

    risk_analyst = Agent(
        client=client,
        name="RiskAnalyst",
        instructions=RISK_PROMPT + "\n\nRespond with valid JSON matching this schema: " + RiskResponse.model_json_schema().__str__(),
        tools=[check_risk_rules],
    )

    obligation_tracker = Agent(
        client=client,
        name="ObligationTracker",
        instructions=OBLIGATION_PROMPT + "\n\nRespond with valid JSON matching this schema: " + ObligationResponse.model_json_schema().__str__(),
        tools=[parse_contract_dates],
    )

    summarizer = Agent(
        client=client,
        name="Summarizer",
        instructions=SUMMARY_PROMPT + "\n\nRespond with valid JSON matching this schema: " + SummaryResponse.model_json_schema().__str__(),
    )

    # Run each agent individually so we can collect structured output from each
    extractor_result = await extractor.run(contract_text)
    extracted_data = ExtractorResponse.model_validate_json(
        str(extractor_result)
    ).extracted_data

    # Feed contract text + extraction results to risk analyst
    risk_input = (
        f"{contract_text}\n\n---\nExtracted data from prior analysis:\n"
        f"{extracted_data.model_dump_json()}"
    )
    risk_result = await risk_analyst.run(risk_input)
    risk_flags = RiskResponse.model_validate_json(str(risk_result)).risk_flags

    # Feed contract text + prior results to obligation tracker
    obligation_input = (
        f"{contract_text}\n\n---\nExtracted data:\n"
        f"{extracted_data.model_dump_json()}"
    )
    obligation_result = await obligation_tracker.run(obligation_input)
    obligations = ObligationResponse.model_validate_json(
        str(obligation_result)
    ).obligations

    # Feed contract text + all prior results to summarizer
    summary_input = (
        f"{contract_text}\n\n---\nExtracted data:\n"
        f"{extracted_data.model_dump_json()}\n\n"
        f"Risk flags:\n{RiskResponse(risk_flags=risk_flags).model_dump_json()}\n\n"
        f"Obligations:\n{ObligationResponse(obligations=obligations).model_dump_json()}"
    )
    summary_result = await summarizer.run(summary_input)
    summary = SummaryResponse.model_validate_json(str(summary_result)).summary

    return AnalysisResult(
        id=uuid.uuid4().hex,
        contract_id=contract_id,
        status=AnalysisStatus.COMPLETED,
        extracted_data=extracted_data,
        risk_flags=risk_flags,
        obligations=obligations,
        summary=summary,
        created_at=datetime.utcnow(),
        completed_at=datetime.utcnow(),
    )


# --- Comparison ---

async def run_comparison(
    analysis_a: AnalysisResult,
    analysis_b: AnalysisResult,
    settings: Settings,
) -> ComparisonResult:
    """Compare two contract analyses side by side."""
    client = create_client(settings)

    comparator = Agent(
        client=client,
        name="Comparator",
        instructions=COMPARISON_PROMPT + "\n\nRespond with valid JSON matching this schema: " + ComparisonResponse.model_json_schema().__str__(),
    )

    comparison_input = (
        f"Contract A (ID: {analysis_a.contract_id}):\n"
        f"{analysis_a.model_dump_json()}\n\n"
        f"Contract B (ID: {analysis_b.contract_id}):\n"
        f"{analysis_b.model_dump_json()}"
    )

    result = await comparator.run(comparison_input)
    parsed = ComparisonResponse.model_validate_json(str(result))

    return ComparisonResult(
        id=uuid.uuid4().hex,
        contract_a_id=analysis_a.contract_id,
        contract_b_id=analysis_b.contract_id,
        term_comparisons=parsed.term_comparisons,
        risk_diff=parsed.risk_diff,
        overall_assessment=parsed.overall_assessment,
        created_at=datetime.utcnow(),
    )
