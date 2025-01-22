import pytest
import os
import json

@pytest.fixture(scope="session")
def load_links():
    """Fixture to load links from the links.json file."""
    links_file = os.path.join(os.getcwd(), "links.json")
    if not os.path.exists(links_file):
        pytest.fail("links.json file is missing.")

    with open(links_file, "r") as f:
        try:
            data = json.load(f)
            return data.get("links", [])
        except json.JSONDecodeError:
            pytest.fail("Invalid JSON format in links.json.")

@pytest.fixture(scope="session")
def test_client():
    """Fixture to provide a test client for the FastAPI app."""
    from app.main import app
    from fastapi.testclient import TestClient

    return TestClient(app)
