from agent_framework import Agent
from pydantic import BaseModel, Field

from app.core.config import Settings
from app.core.models import Obligation
from app.agents.tools.common import create_client, parse_contract_dates


OBLIGATION_PROMPT = """\
You are a contract obligation tracking specialist. Your job is to extract every \
deadline, deliverable, milestone, renewal date, notice period, and compliance \
requirement from a legal contract.

For each obligation found, provide:
- **party**: Which party is responsible (use the actual party name from the contract).
- **description**: A clear description of what must be done or delivered.
- **due_date**: The specific date or relative timing (e.g., "within 30 days of execution", "2025-12-31"). Use ISO format where possible.
- **recurring**: Whether this obligation repeats (true/false).
- **frequency**: If recurring, how often (e.g., "monthly", "quarterly", "annually").
- **status**: Set to "active" for all extracted obligations.

Pay special attention to:
- Contract renewal and termination notice deadlines
- Payment schedules and financial reporting requirements
- Deliverable milestones and acceptance periods
- Insurance certificate delivery requirements
- Compliance certifications and audit deadlines
- Post-termination obligations and survival clauses

Extract all obligations for ALL parties, not just one side. Include both \
explicit dates and relative deadlines tied to contract events.
"""


class ObligationResponse(BaseModel):
    """Structured output from the ObligationTracker agent."""
    obligations: list[Obligation] = Field(default_factory=list)


def create_obligation_agent(settings: Settings) -> Agent:
    """Create a standalone ObligationTracker agent."""
    client = create_client(settings)
    return Agent(
        client=client,
        name="ObligationTracker",
        instructions=OBLIGATION_PROMPT,
        tools=[parse_contract_dates],
    )


async def run_obligation_tracker(contract_text: str, prior_context: str, settings: Settings) -> list[Obligation]:
    """Run the ObligationTracker agent and return parsed obligations."""
    agent = create_obligation_agent(settings)
    input_text = f"{contract_text}\n\n---\nExtracted data:\n{prior_context}"
    result = await agent.run(input_text, options={"response_format": ObligationResponse})
    return result.value.obligations
