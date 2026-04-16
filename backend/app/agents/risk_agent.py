from agent_framework import Agent
from pydantic import BaseModel, Field

from app.core.config import Settings
from app.core.models import RiskFlag
from app.agents.tools.common import create_client
from app.agents.tools.risk import check_risk_rules


RISK_PROMPT = """\
You are a contract risk analysis specialist. Your job is to identify and flag \
potentially risky, unusual, or one-sided clauses in a legal contract.

Analyze the contract text for risks across these categories:
- **termination**: One-sided termination rights, termination for convenience by only one party, short cure periods.
- **liability**: Uncapped liability, asymmetric liability limits, broad liability assumptions.
- **intellectual_property**: IP assignment to one party, broad license grants, loss of IP rights on termination.
- **confidentiality**: Overly broad confidentiality obligations, long survival periods, one-sided NDA terms.
- **indemnification**: Uncapped indemnification, broad indemnification triggers, one-sided hold harmless.
- **change_of_control**: Restrictive change of control provisions, consent requirements for assignment.
- **exclusivity**: Exclusive dealing arrangements, broad exclusivity scopes, long exclusivity periods.
- **competition**: Non-compete clauses, non-solicit restrictions, broad geographic or temporal scope.
- **insurance**: Missing insurance requirements, inadequate coverage minimums.
- **audit**: Broad audit rights, short notice periods, unrestricted audit scope.

For each risk found, provide:
- **category**: One of the categories above.
- **severity**: "high", "medium", or "low" based on potential business impact.
- **clause_text**: The exact text or close paraphrase of the problematic clause.
- **explanation**: A plain-English explanation of why this clause is risky.
- **mitigation**: A suggested negotiation point or mitigation strategy.

Flag HIGH severity for clauses that could expose the organization to significant \
financial loss, legal liability, or loss of key rights. Flag MEDIUM for clauses that \
are unfavorable but manageable. Flag LOW for minor concerns or unusual but \
non-critical terms.

Only flag genuine risks. Do not flag standard or balanced provisions.
"""


class RiskResponse(BaseModel):
    """Structured output from the RiskAnalyst agent."""
    risk_flags: list[RiskFlag] = Field(default_factory=list)


def create_risk_agent(settings: Settings) -> Agent:
    """Create a standalone RiskAnalyst agent."""
    client = create_client(settings)
    return Agent(
        client=client,
        name="RiskAnalyst",
        instructions=RISK_PROMPT,
        tools=[check_risk_rules],
    )


async def run_risk_analyst(contract_text: str, prior_context: str, settings: Settings) -> list[RiskFlag]:
    """Run the RiskAnalyst agent and return parsed risk flags."""
    agent = create_risk_agent(settings)
    input_text = f"{contract_text}\n\n---\nExtracted data from prior analysis:\n{prior_context}"
    result = await agent.run(input_text, options={"response_format": RiskResponse})
    return result.value.risk_flags
