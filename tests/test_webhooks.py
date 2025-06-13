import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_webhook_endpoint_success():
    response = client.post("/api/v1/webhooks/job-analysis", json={"data": "test data"})
    assert response.status_code == 200
    assert response.json() == {"message": "Webhook received successfully"}

def test_webhook_endpoint_invalid_data():
    response = client.post("/api/v1/webhooks/job-analysis", json={"invalid": "data"})
    assert response.status_code == 422  # Unprocessable Entity
    assert "detail" in response.json()  # Check for validation error details

def test_webhook_endpoint_missing_data():
    response = client.post("/api/v1/webhooks/job-analysis")
    assert response.status_code == 422  # Unprocessable Entity
    assert "detail" in response.json()  # Check for validation error details

def test_webhook_endpoint_error_handling():
    response = client.post("/api/v1/webhooks/job-analysis", json={"data": "trigger error"})
    assert response.status_code == 500  # Internal Server Error
    assert "detail" in response.json()  # Check for error details in response