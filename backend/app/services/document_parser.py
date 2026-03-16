import aiofiles
from pathlib import Path

from app.core.config import Settings


async def parse_text_file(file_path: str) -> str:
    """Read a .txt file directly. Used for local dev and CUAD .txt contracts."""
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    async with aiofiles.open(path, mode="r", encoding="utf-8", errors="replace") as f:
        return await f.read()


async def parse_with_doc_intelligence(file_bytes: bytes, settings: Settings) -> str:
    """Parse a document using Azure AI Document Intelligence (prebuilt-read model)."""
    from azure.ai.documentintelligence.aio import DocumentIntelligenceClient
    from azure.core.credentials import AzureKeyCredential

    client = DocumentIntelligenceClient(
        endpoint=settings.doc_intelligence_endpoint,
        credential=AzureKeyCredential(settings.doc_intelligence_key),
    )
    async with client:
        poller = await client.begin_analyze_document(
            "prebuilt-read",
            body=file_bytes,
            content_type="application/octet-stream",
        )
        result = await poller.result()

    # Concatenate all page content
    content = ""
    if result.content:
        content = result.content
    return content


async def parse_document(file_path_or_bytes: str | bytes, settings: Settings) -> str:
    """Parse a document. Uses local .txt reader or Azure Doc Intelligence based on settings."""
    if settings.use_local_parser:
        if isinstance(file_path_or_bytes, bytes):
            return file_path_or_bytes.decode("utf-8", errors="replace")
        return await parse_text_file(file_path_or_bytes)
    else:
        if isinstance(file_path_or_bytes, str):
            async with aiofiles.open(file_path_or_bytes, mode="rb") as f:
                file_bytes = await f.read()
        else:
            file_bytes = file_path_or_bytes
        return await parse_with_doc_intelligence(file_bytes, settings)
