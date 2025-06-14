# pytest configuration and fixtures for testing

import pytest

@pytest.fixture(scope="session")
def test_client():
    from fastapi.testclient import TestClient
    from app.main import app

    client = TestClient(app)
    yield client  # This will be the test client for the tests
