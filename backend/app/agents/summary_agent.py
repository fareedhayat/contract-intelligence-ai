from agent_framework import Agent
from pydantic import BaseModel

from app.core.config import Settings
from app.core.models import ContractSummary
from app.agents.tools.common import create_client


SUMMARY_PROMPT = """\
You are a contract summarization specialist. Your job is to produce a clear, \
concise summary of a legal contract that a non-legal business stakeholder can \
understand and act on.

Produce the following:
- **executive_summary**: A 2-3 paragraph plain-English summary covering:
  - What the contract is about and who the parties are
  - Key financial commitments and duration
  - The most important obligations and restrictions
  - Any notable risks or unusual terms
  Write for a business audience — avoid legal jargon, explain implications.

- **key_provisions**: A list of 5-10 bullet points highlighting the most important \
  terms and conditions. Each should be a single clear sentence.

- **notable_clauses**: A list of clauses that are unusual, particularly favorable, \
  or particularly unfavorable compared to standard commercial terms. Include a brief \
  note on why each is notable.

Be accurate and faithful to the contract text. Do not add information that is not \
in the document. Focus on what matters most for business decision-making.
"""


class SummaryResponse(BaseModel):
    """Structured output from the Summarizer agent."""
    summary: ContractSummary


def create_summary_agent(settings: Settings) -> Agent:
    """Create a standalone Summarizer agent."""
    client = create_client(settings)
    return Agent(
        client=client,
        name="Summarizer",
        instructions=SUMMARY_PROMPT,
    )


async def run_summarizer(contract_text: str, prior_context: str, settings: Settings) -> ContractSummary:
    """Run the Summarizer agent and return parsed contract summary."""
    agent = create_summary_agent(settings)
    input_text = f"{contract_text}\n\n---\n{prior_context}"
    result = await agent.run(input_text, options={"response_format": SummaryResponse})
    return result.value.summary
