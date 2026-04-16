from agent_framework import Agent
from pydantic import BaseModel

from app.core.config import Settings
from app.core.models import ExtractedData
from app.agents.tools.common import create_client, parse_contract_dates
from app.agents.tools.extraction import lookup_cuad_ground_truth


EXTRACTOR_PROMPT = """\
You are a contract data extraction specialist. Your job is to read the full \
text of a legal contract and extract structured information.

Extract the following fields:
- **parties**: List of all named parties to the agreement (company names, individuals).
- **effective_date**: The date the contract takes effect. Use ISO format (YYYY-MM-DD) if possible, otherwise use the date as written.
- **expiration_date**: The date the contract expires or terminates. Use ISO format if possible.
- **governing_law**: The state, country, or jurisdiction whose laws govern the contract.
- **contract_type**: The type of agreement (e.g., "License Agreement", "Service Agreement", "Distribution Agreement").
- **financial_terms**: A list of financial commitments. Each should have:
  - term_type: what kind of financial term (e.g., "minimum commitment", "royalty", "service fee")
  - value: the numeric amount (null if not specified)
  - currency: the currency code (default "USD")
  - description: a brief description of the financial term

Be thorough. Read the entire document. If a field is not present in the contract, \
leave it as null or an empty list. Do not guess or fabricate information — only \
extract what is explicitly stated in the text.
"""


class ExtractorResponse(BaseModel):
    """Structured output from the DataExtractor agent."""
    extracted_data: ExtractedData


def create_extractor_agent(settings: Settings) -> Agent:
    """Create a standalone DataExtractor agent."""
    client = create_client(settings)
    return Agent(
        client=client,
        name="DataExtractor",
        instructions=EXTRACTOR_PROMPT,
        tools=[parse_contract_dates, lookup_cuad_ground_truth],
    )


async def run_extractor(contract_text: str, settings: Settings) -> ExtractedData:
    """Run the DataExtractor agent and return parsed extracted data."""
    agent = create_extractor_agent(settings)
    result = await agent.run(contract_text, options={"response_format": ExtractorResponse})
    return result.value.extracted_data
