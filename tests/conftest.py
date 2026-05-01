import pytest

@pytest.fixture(scope="session")
def test_client():
    from app.main import app
    from fastapi.testclient import TestClient
    return TestClient(app)
