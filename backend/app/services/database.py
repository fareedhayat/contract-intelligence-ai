import uuid
from datetime import datetime
from functools import lru_cache

from azure.cosmos.aio import CosmosClient
from azure.cosmos import PartitionKey, exceptions

from app.core.config import Settings
from app.core.models import (
    ContractDocument,
    AnalysisResult,
    AnalysisStatus,
    ComparisonResult,
)


CONTRACTS_CONTAINER = "contracts"
ANALYSIS_CONTAINER = "analysis"
COMPARISONS_CONTAINER = "comparisons"


_cosmos_client: CosmosClient | None = None


def get_cosmos_client(settings: Settings) -> CosmosClient:
    """Get or create a cached Cosmos DB client."""
    global _cosmos_client
    if _cosmos_client is None:
        _cosmos_client = CosmosClient(
            url=settings.cosmos_endpoint,
            credential=settings.cosmos_key,
        )
    return _cosmos_client


async def ensure_database(settings: Settings):
    """Create database and containers if they don't exist."""
    client = get_cosmos_client(settings)
    database = await client.create_database_if_not_exists(id=settings.cosmos_database)

    await database.create_container_if_not_exists(
        id=CONTRACTS_CONTAINER,
        partition_key=PartitionKey(path="/id"),
    )
    await database.create_container_if_not_exists(
        id=ANALYSIS_CONTAINER,
        partition_key=PartitionKey(path="/contract_id"),
    )
    await database.create_container_if_not_exists(
        id=COMPARISONS_CONTAINER,
        partition_key=PartitionKey(path="/id"),
    )


async def _get_container(settings: Settings, container_name: str):
    client = get_cosmos_client(settings)
    database = client.get_database_client(settings.cosmos_database)
    return database.get_container_client(container_name)


# --- Contracts ---

async def save_contract(contract: ContractDocument, settings: Settings):
    """Upsert a contract document."""
    container = await _get_container(settings, CONTRACTS_CONTAINER)
    await container.upsert_item(contract.model_dump(mode="json"))


async def get_contract(contract_id: str, settings: Settings) -> ContractDocument | None:
    """Get a contract by ID."""
    container = await _get_container(settings, CONTRACTS_CONTAINER)
    try:
        item = await container.read_item(item=contract_id, partition_key=contract_id)
        return ContractDocument(**item)
    except exceptions.CosmosResourceNotFoundError:
        return None


async def list_contracts(settings: Settings, skip: int = 0, limit: int = 20) -> tuple[list[ContractDocument], int]:
    """List contracts with pagination. Returns (contracts, total_count)."""
    container = await _get_container(settings, CONTRACTS_CONTAINER)

    count_query = container.query_items(
        query="SELECT VALUE COUNT(1) FROM c",
        enable_cross_partition_query=True,
    )
    total = 0
    async for item in count_query:
        total = item

    query = container.query_items(
        query="SELECT * FROM c ORDER BY c.upload_date DESC OFFSET @skip LIMIT @limit",
        parameters=[{"name": "@skip", "value": skip}, {"name": "@limit", "value": limit}],
        enable_cross_partition_query=True,
    )
    contracts = []
    async for item in query:
        contracts.append(ContractDocument(**item))

    return contracts, total


async def delete_contract(contract_id: str, settings: Settings):
    """Delete a contract and its analysis results."""
    container = await _get_container(settings, CONTRACTS_CONTAINER)
    try:
        await container.delete_item(item=contract_id, partition_key=contract_id)
    except exceptions.CosmosResourceNotFoundError:
        pass

    # Also delete associated analysis
    analysis_container = await _get_container(settings, ANALYSIS_CONTAINER)
    query = analysis_container.query_items(
        query="SELECT * FROM c WHERE c.contract_id = @cid",
        parameters=[{"name": "@cid", "value": contract_id}],
        enable_cross_partition_query=True,
    )
    async for item in query:
        await analysis_container.delete_item(item=item["id"], partition_key=item["contract_id"])


# --- Analysis ---

async def save_analysis(result: AnalysisResult, settings: Settings):
    """Upsert an analysis result."""
    container = await _get_container(settings, ANALYSIS_CONTAINER)
    await container.upsert_item(result.model_dump(mode="json"))


async def get_analysis(contract_id: str, settings: Settings) -> AnalysisResult | None:
    """Get the latest analysis result for a contract."""
    container = await _get_container(settings, ANALYSIS_CONTAINER)
    query = container.query_items(
        query="SELECT * FROM c WHERE c.contract_id = @cid ORDER BY c.created_at DESC",
        parameters=[{"name": "@cid", "value": contract_id}],
        enable_cross_partition_query=True,
    )
    async for item in query:
        return AnalysisResult(**item)
    return None


async def update_analysis_status(
    contract_id: str, status: AnalysisStatus, settings: Settings, error_message: str | None = None
):
    """Update the status of an analysis result."""
    result = await get_analysis(contract_id, settings)
    if result is None:
        return
    result.status = status
    if status == AnalysisStatus.COMPLETED:
        result.completed_at = datetime.utcnow()
    if error_message:
        result.error_message = error_message
    await save_analysis(result, settings)


# --- Comparisons ---

async def save_comparison(comparison: ComparisonResult, settings: Settings):
    """Upsert a comparison result."""
    container = await _get_container(settings, COMPARISONS_CONTAINER)
    await container.upsert_item(comparison.model_dump(mode="json"))


async def get_comparison(comparison_id: str, settings: Settings) -> ComparisonResult | None:
    """Get a comparison by ID."""
    container = await _get_container(settings, COMPARISONS_CONTAINER)
    try:
        item = await container.read_item(item=comparison_id, partition_key=comparison_id)
        return ComparisonResult(**item)
    except exceptions.CosmosResourceNotFoundError:
        return None


# --- Dashboard ---

async def get_dashboard_stats(settings: Settings) -> dict:
    """Get aggregated stats for the dashboard."""
    container = await _get_container(settings, CONTRACTS_CONTAINER)
    analysis_container = await _get_container(settings, ANALYSIS_CONTAINER)

    # Total contracts
    total_query = container.query_items(
        query="SELECT VALUE COUNT(1) FROM c",
        enable_cross_partition_query=True,
    )
    total_contracts = 0
    async for item in total_query:
        total_contracts = item

    # Analysis counts by status
    status_query = analysis_container.query_items(
        query="SELECT c.status, COUNT(1) as count FROM c GROUP BY c.status",
        enable_cross_partition_query=True,
    )
    status_counts = {}
    async for item in status_query:
        status_counts[item["status"]] = item["count"]

    # High risk count
    risk_query = analysis_container.query_items(
        query="SELECT VALUE COUNT(1) FROM c WHERE ARRAY_LENGTH(c.risk_flags) > 0",
        enable_cross_partition_query=True,
    )
    contracts_with_risks = 0
    async for item in risk_query:
        contracts_with_risks = item

    return {
        "total_contracts": total_contracts,
        "analyzed": status_counts.get("completed", 0),
        "pending": status_counts.get("pending", 0) + status_counts.get("in_progress", 0),
        "failed": status_counts.get("failed", 0),
        "contracts_with_risks": contracts_with_risks,
    }
