import pytest


@pytest.mark.asyncio
async def test_health_check(client):
    response = await client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "contract-intelligence-ai"


@pytest.mark.asyncio
async def test_list_contracts_empty(client):
    response = await client.get("/api/contracts", params={"skip": 0, "limit": 10})
    assert response.status_code == 200
    data = response.json()
    assert "contracts" in data
    assert "total" in data


@pytest.mark.asyncio
async def test_get_contract_not_found(client):
    response = await client.get("/api/contracts/nonexistent-id")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_get_analysis_not_found(client):
    response = await client.get("/api/analysis/nonexistent-id")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_get_analysis_status_not_found(client):
    response = await client.get("/api/analysis/nonexistent-id/status")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_dashboard_stats(client):
    response = await client.get("/api/analysis/dashboard/stats")
    assert response.status_code == 200
    data = response.json()
    assert "total_contracts" in data
    assert "analyzed" in data
    assert "pending" in data
    assert "failed" in data


@pytest.mark.asyncio
async def test_compare_missing_analysis(client):
    response = await client.post(
        "/api/compare",
        json={"contract_a_id": "fake-a", "contract_b_id": "fake-b"},
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_get_comparison_not_found(client):
    response = await client.get("/api/compare/nonexistent-id")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_list_obligations(client):
    response = await client.get("/api/obligations", params={"skip": 0, "limit": 10})
    assert response.status_code == 200
    data = response.json()
    assert "obligations" in data
    assert "total" in data


@pytest.mark.asyncio
async def test_upcoming_obligations(client):
    response = await client.get("/api/obligations/upcoming", params={"days": 30})
    assert response.status_code == 200
    data = response.json()
    assert "obligations" in data


@pytest.mark.asyncio
async def test_cuad_contracts_list(client):
    response = await client.get("/api/cuad/contracts", params={"skip": 0, "limit": 10})
    # May return 404 if CUAD dataset not downloaded — both are valid
    assert response.status_code in (200, 404)


@pytest.mark.asyncio
async def test_cuad_contract_types(client):
    response = await client.get("/api/cuad/contract-types")
    assert response.status_code in (200, 404)
