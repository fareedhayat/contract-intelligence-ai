import uuid
from datetime import datetime

from agent_framework import Agent
from pydantic import BaseModel, Field

from app.core.config import Settings
from app.core.models import AnalysisResult, ComparisonResult, TermComparison
from app.agents.tools.common import create_client


COMPARISON_PROMPT = """\
You are a contract comparison specialist. Your job is to compare two contracts \
and produce a structured analysis of their differences.

You will receive two contract analysis results. Compare them across all key dimensions.

For each significant difference, provide a term comparison with:
- **term_name**: The name of the term or clause being compared (e.g., "Duration", "Liability Cap", "Termination Rights").
- **contract_a_value**: How Contract A handles this term.
- **contract_b_value**: How Contract B handles this term.
- **difference**: A plain-English description of the difference.
- **advantage**: Which contract is more favorable for this term ("contract_a", "contract_b", or "neutral").

Also provide:
- **risk_diff**: A summary of how the risk profiles differ between the two contracts.
- **overall_assessment**: A 2-3 sentence recommendation on which contract is more favorable overall and why.

Be specific and cite actual terms. Focus on differences that have real business impact — \
don't flag trivial formatting or wording differences.
"""


class ComparisonResponse(BaseModel):
    """Structured output from the Comparison agent."""
    term_comparisons: list[TermComparison] = Field(default_factory=list)
    risk_diff: str = ""
    overall_assessment: str = ""


def create_comparison_agent(settings: Settings) -> Agent:
    """Create a standalone Comparator agent."""
    client = create_client(settings)
    return Agent(
        client=client,
        name="Comparator",
        instructions=COMPARISON_PROMPT,
    )


async def run_comparison(
    analysis_a: AnalysisResult,
    analysis_b: AnalysisResult,
    settings: Settings,
) -> ComparisonResult:
    """Run the Comparator agent and return parsed comparison result."""
    agent = create_comparison_agent(settings)

    comparison_input = (
        f"Contract A (ID: {analysis_a.contract_id}):\n"
        f"{analysis_a.model_dump_json()}\n\n"
        f"Contract B (ID: {analysis_b.contract_id}):\n"
        f"{analysis_b.model_dump_json()}"
    )

    result = await agent.run(comparison_input, options={"response_format": ComparisonResponse})
    parsed = result.value

    return ComparisonResult(
        id=uuid.uuid4().hex,
        contract_a_id=analysis_a.contract_id,
        contract_b_id=analysis_b.contract_id,
        term_comparisons=parsed.term_comparisons,
        risk_diff=parsed.risk_diff,
        overall_assessment=parsed.overall_assessment,
        created_at=datetime.utcnow(),
    )
