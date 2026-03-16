import uuid
import aiofiles
from pathlib import Path

from app.core.config import Settings


async def save_file_local(file_bytes: bytes, filename: str, settings: Settings) -> str:
    """Save a file to local filesystem under data/uploads/."""
    upload_dir = Path(settings.cuad_data_path) / "uploads"
    upload_dir.mkdir(parents=True, exist_ok=True)

    # Add unique prefix to avoid collisions
    unique_name = f"{uuid.uuid4().hex[:8]}_{filename}"
    file_path = upload_dir / unique_name

    async with aiofiles.open(file_path, mode="wb") as f:
        await f.write(file_bytes)

    return str(file_path)


async def save_file_blob(file_bytes: bytes, filename: str, settings: Settings) -> str:
    """Upload a file to Azure Blob Storage. Returns the blob URL."""
    from azure.storage.blob.aio import BlobServiceClient

    unique_name = f"{uuid.uuid4().hex[:8]}_{filename}"

    blob_service = BlobServiceClient.from_connection_string(settings.blob_connection_string)
    async with blob_service:
        container = blob_service.get_container_client(settings.blob_container_name)
        blob = container.get_blob_client(unique_name)
        await blob.upload_blob(file_bytes, overwrite=True)
        return blob.url


async def save_file(file_bytes: bytes, filename: str, settings: Settings) -> str:
    """Save a file. Routes to local filesystem or Azure Blob based on settings."""
    if settings.use_local_storage:
        return await save_file_local(file_bytes, filename, settings)
    else:
        return await save_file_blob(file_bytes, filename, settings)


async def read_file_local(file_path: str) -> bytes:
    """Read a file from local filesystem."""
    async with aiofiles.open(file_path, mode="rb") as f:
        return await f.read()


async def read_file_blob(blob_url: str, settings: Settings) -> bytes:
    """Read a file from Azure Blob Storage."""
    from azure.storage.blob.aio import BlobServiceClient

    blob_service = BlobServiceClient.from_connection_string(settings.blob_connection_string)
    async with blob_service:
        blob = blob_service.get_blob_client_from_url(blob_url)
        stream = await blob.download_blob()
        return await stream.readall()
