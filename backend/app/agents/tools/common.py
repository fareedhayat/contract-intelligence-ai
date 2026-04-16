import re
from typing import Annotated

from agent_framework import tool
from agent_framework.openai import OpenAIChatClient
from pydantic import Field

from app.core.config import Settings


def create_client(settings: Settings) -> OpenAIChatClient:
    """Create an Azure OpenAI chat client using API key authentication."""
    return OpenAIChatClient(
        model=settings.azure_openai_deployment,
        azure_endpoint=settings.azure_openai_endpoint,
        api_version=settings.azure_openai_api_version,
        api_key=settings.azure_openai_api_key,
    )


@tool
def parse_contract_dates(
    text: Annotated[str, Field(description="Text containing dates to extract and normalize")],
) -> str:
    """Extract and normalize dates found in contract text.
    Returns a list of identified dates with context."""
    date_patterns = [
        (r'\b(\d{1,2}[/\-]\d{1,2}[/\-]\d{2,4})\b', "numeric date"),
        (r'\b(January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},?\s+\d{4}\b', "full date"),
        (r'\b(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\.?\s+\d{1,2},?\s+\d{4}\b', "abbreviated date"),
        (r'\b\d{4}[/\-]\d{1,2}[/\-]\d{1,2}\b', "ISO date"),
    ]

    found_dates = []
    for pattern, label in date_patterns:
        matches = re.finditer(pattern, text, re.IGNORECASE)
        for match in matches:
            start = max(0, match.start() - 50)
            end = min(len(text), match.end() + 50)
            context = text[start:end].replace("\n", " ").strip()
            found_dates.append(f"{match.group()} ({label}) — ...{context}...")

    if not found_dates:
        return "No dates found in the provided text."
    return "\n".join(found_dates)
