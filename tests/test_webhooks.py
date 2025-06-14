import pytest
from unittest.mock import Mock, patch
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


# ===== BASIC WEBHOOK ENDPOINT TESTS =====

def test_webhook_health_endpoint():
    """Test webhook health check endpoint availability"""
    response = client.get("/api/v1/webhooks/health")

    assert response.status_code == 200
    response_data = response.json()
    assert response_data["status"] == "healthy"
    assert response_data["service"] == "webhook-handler"


# ===== JOB ANALYSIS WEBHOOK - SUCCESS SCENARIOS =====

@patch('app.core.security.verify_api_key')  # Mock authentication
@patch('app.api.v1.endpoints.webhooks.MultiLLMJobAnalyzer')
@patch('app.api.v1.endpoints.webhooks.verify_webhook_signature_middleware')
def test_job_analysis_webhook_sync_success(mock_verify, mock_analyzer, mock_auth):
    """Test successful synchronous job analysis with complete workflow"""
    # Arrange: Mock authentication and all dependencies for successful flow
    mock_auth.return_value = True  # Allow authentication to pass
    mock_verify.return_value = None
    mock_analyzer_instance = Mock()
    mock_analyzer.return_value = mock_analyzer_instance
    mock_analyzer_instance.scraper.scrape_url.return_value = {
        "success": True,
        "content": "job content"
    }
    mock_analyzer_instance.analyze_job_post.return_value = "analyzed content"

    with patch('app.api.v1.endpoints.webhooks.post_process_llm_output') as mock_post_process:
        mock_post_process.return_value = {"processed": "result"}

        # Act: Send synchronous job analysis request with auth header
        response = client.post("/api/v1/webhooks/job-analysis",
                               json={
                                   "job_id": "test-123",
                                   "url": "https://example.com/job",
                                   "async_processing": False
                               },
                               headers={"X-API-Key": "test-api-key"})

    # Assert: Verify successful completion
    assert response.status_code == 200
    response_data = response.json()
    assert response_data["status"] == "completed"
    assert response_data["job_id"] == "test-123"
    assert "result" in response_data


@patch('app.core.security.verify_api_key')  # Mock authentication
@patch('app.api.v1.endpoints.webhooks.MultiLLMJobAnalyzer')
@patch('app.api.v1.endpoints.webhooks.verify_webhook_signature_middleware')
@patch('app.api.v1.endpoints.webhooks.process_job_in_background')
def test_job_analysis_webhook_async_success(mock_background_process, mock_verify, mock_analyzer, mock_auth):
    """Test successful asynchronous job analysis with background processing"""
    # Arrange: Mock authentication and dependencies for async flow
    mock_auth.return_value = True  # Allow authentication to pass
    mock_verify.return_value = None
    mock_analyzer_instance = Mock()
    mock_analyzer.return_value = mock_analyzer_instance

    # Act: Send asynchronous job analysis request with auth header
    response = client.post("/api/v1/webhooks/job-analysis",
                           json={
                               "job_id": "test-async-123",
                               "url": "https://example.com/job",
                               "async_processing": True,
                               "callback_url": "https://callback.example.com"
                           },
                           headers={"X-API-Key": "test-api-key"})

    # Assert: Verify async job acceptance and background task initiation
    response_data = response.json()
    assert response.status_code == 200
    assert response_data["status"] == "accepted"
    assert response_data["job_id"] == "test-async-123"
    assert "background" in response_data["message"]
    mock_background_process.assert_called_once()


# ===== JOB ANALYSIS WEBHOOK - ERROR SCENARIOS =====

@patch('app.core.security.verify_api_key')  # Mock authentication
@patch('app.api.v1.endpoints.webhooks.MultiLLMJobAnalyzer')
@patch('app.api.v1.endpoints.webhooks.verify_webhook_signature_middleware')
def test_job_analysis_webhook_scraping_failure(mock_verify, mock_analyzer, mock_auth):
    """Test job analysis when web scraping fails"""
    # Arrange: Mock authentication and scraping failure
    mock_auth.return_value = True  # Allow authentication to pass
    mock_verify.return_value = None
    mock_analyzer_instance = Mock()
    mock_analyzer.return_value = mock_analyzer_instance
    mock_analyzer_instance.scraper.scrape_url.return_value = {
        "success": False,
        "error": "Failed to scrape"
    }

    # Act: Send request for URL that fails scraping with auth header
    response = client.post("/api/v1/webhooks/job-analysis",
                           json={
                               "job_id": "test-fail-123",
                               "url": "https://invalid-url.com",
                               "async_processing": False
                           },
                           headers={"X-API-Key": "test-api-key"})

    # Assert: Verify proper error handling for scraping failure
    assert response.status_code == 400
    assert "Failed to scrape job data" in response.json()["detail"]


def test_job_analysis_webhook_authentication_failure():
    """Test webhook security when authentication fails"""
    # Act: Send request without authentication header
    response = client.post("/api/v1/webhooks/job-analysis", json={
        "job_id": "test-123",
        "url": "https://example.com/job"
    })

    # Assert: Verify authentication rejection
    assert response.status_code == 401


@patch('app.core.security.verify_api_key')  # Mock authentication
@patch('app.api.v1.endpoints.webhooks.verify_webhook_signature_middleware')
def test_job_analysis_webhook_signature_verification_failure(mock_verify, mock_auth):
    """Test webhook security when signature verification fails"""
    # Arrange: Mock authentication success but signature verification failure
    mock_auth.return_value = True  # Allow authentication to pass
    mock_verify.side_effect = Exception("Invalid signature")

    # Act: Send request with invalid signature but valid auth
    response = client.post("/api/v1/webhooks/job-analysis",
                           json={
                               "job_id": "test-123",
                               "url": "https://example.com/job"
                           },
                           headers={"X-API-Key": "test-api-key"})

    # Assert: Verify security rejection
    assert response.status_code == 500


@patch('app.core.security.verify_api_key')  # Mock authentication
@patch('app.api.v1.endpoints.webhooks.MultiLLMJobAnalyzer')
@patch('app.api.v1.endpoints.webhooks.verify_webhook_signature_middleware')
def test_job_analysis_webhook_analyzer_exception(mock_verify, mock_analyzer, mock_auth):
    """Test error handling when analyzer initialization fails"""
    # Arrange: Mock authentication success but analyzer initialization failure
    mock_auth.return_value = True  # Allow authentication to pass
    mock_verify.return_value = None
    mock_analyzer.side_effect = Exception("Analyzer initialization failed")

    # Act: Send request when analyzer fails to initialize
    response = client.post("/api/v1/webhooks/job-analysis",
                           json={
                               "job_id": "test-exception-123",
                               "url": "https://example.com/job",
                               "async_processing": False
                           },
                           headers={"X-API-Key": "test-api-key"})

    # Assert: Verify proper error handling for system failures
    assert response.status_code == 500
    assert "Internal server error" in response.json()["detail"]


# ===== REQUEST VALIDATION TESTS =====

@patch('app.core.security.verify_api_key')  # Mock authentication
def test_job_analysis_webhook_missing_required_fields(mock_auth):
    """Test request validation for missing required fields"""
    # Arrange: Mock authentication success
    mock_auth.return_value = True

    # Act: Send request missing required 'url' field but with auth
    response = client.post("/api/v1/webhooks/job-analysis",
                           json={
                               "job_id": "test-123"
                               # Missing url field
                           },
                           headers={"X-API-Key": "test-api-key"})

    # Assert: Verify validation error for missing fields
    assert response.status_code == 422
    assert "detail" in response.json()


@patch('app.core.security.verify_api_key')  # Mock authentication
def test_job_analysis_webhook_invalid_url_format(mock_auth):
    """Test request validation for malformed URLs"""
    # Arrange: Mock authentication success
    mock_auth.return_value = True

    # Act: Send request with invalid URL format but with auth
    response = client.post("/api/v1/webhooks/job-analysis",
                           json={
                               "job_id": "test-123",
                               "url": "not-a-valid-url"
                           },
                           headers={"X-API-Key": "test-api-key"})

    # Assert: Verify validation error for invalid URL format
    assert response.status_code == 422
    assert "detail" in response.json()


@patch('app.core.security.verify_api_key')  # Mock authentication
@pytest.mark.parametrize("invalid_data", [
    {"job_id": "", "url": "https://example.com"},      # Empty job_id
    {"job_id": "test", "url": ""},                     # Empty URL
    {"job_id": None, "url": "https://example.com"},    # None job_id
    {"job_id": "test", "url": None},                   # None URL
])
def test_job_analysis_webhook_invalid_parameters(invalid_data, mock_auth):
    """Test webhook validation with various invalid parameter combinations"""
    # Arrange: Mock authentication success
    mock_auth.return_value = True

    # Act: Send request with invalid parameter combinations but with auth
    response = client.post("/api/v1/webhooks/job-analysis",
                           json=invalid_data,
                           headers={"X-API-Key": "test-api-key"})

    # Assert: Verify validation errors for all invalid combinations
    assert response.status_code == 422
    assert "detail" in response.json()


@patch('app.core.security.verify_api_key')  # Mock authentication
def test_job_analysis_webhook_no_request_body(mock_auth):
    """Test webhook validation when no request body is provided"""
    # Arrange: Mock authentication success
    mock_auth.return_value = True

    # Act: Send request without any JSON body but with auth
    response = client.post("/api/v1/webhooks/job-analysis",
                           headers={"X-API-Key": "test-api-key"})

    # Assert: Verify validation error for missing request body
    assert response.status_code == 422
    assert "detail" in response.json()
