import pytest
from httpx import ASGITransport, AsyncClient

from app.core.config import Settings
from app.api.main import app


@pytest.fixture
def settings():
    return Settings()


@pytest.fixture
def data_path(settings):
    return settings.cuad_data_path


@pytest.fixture
async def client():
    """Async test client for FastAPI app."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        yield c
