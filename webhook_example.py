#!/usr/bin/env python3
"""
Example script demonstrating how to make webhook calls with proper HMAC signatures
and how to verify callback signatures.

Usage:
    python webhook_example.py
"""

import json
import hmac
import hashlib
import requests
from app.utils.llm_data_postprocessing import verify_callback_signature


def generate_webhook_signature(payload: str, secret: str) -> str:
    """Generate HMAC-SHA256 signature for webhook payload."""
    signature = hmac.new(
        secret.encode('utf-8'),
        payload.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()
    return f"sha256={signature}"


def send_job_analysis_webhook():
    """Example: Send job analysis webhook with proper signature."""

    # Configuration
    webhook_url = "http://localhost:8000/api/v1/webhooks/job-analysis"
    # Should match WEBHOOK_SECRET in .env
    webhook_secret = "your-webhook-secret-key"

    # Create payload
    payload_data = {
        "job_id": "example-job-123",
        "url": "https://example.com/job-posting",
        "async_processing": True,
        "callback_url": "https://your-app.com/callback"
    }

    # Convert to JSON string (ensure consistent formatting)
    payload_json = json.dumps(payload_data, separators=(',', ':'))

    # Generate signature
    signature = generate_webhook_signature(payload_json, webhook_secret)

    # Prepare headers
    headers = {
        "Content-Type": "application/json",
        "X-Webhook-Signature": signature
    }

    print(f"Sending webhook request...")
    print(f"URL: {webhook_url}")
    print(f"Payload: {payload_json}")
    print(f"Signature: {signature}")

    try:
        # Send request
        response = requests.post(
            webhook_url, data=payload_json, headers=headers)
        print(f"Response Status: {response.status_code}")
        print(f"Response Body: {response.json()}")
        return response

    except Exception as e:
        print(f"Error sending webhook: {e}")
        return None


def example_callback_handler(request_body: str, signature_header: str):
    """Example: How to handle incoming callbacks with signature verification."""

    webhook_secret = "your-webhook-secret-key"  # Should match WEBHOOK_SECRET

    # Verify signature
    if verify_callback_signature(request_body, signature_header, webhook_secret):
        print("✅ Callback signature verified successfully!")

        # Parse and process callback data
        try:
            callback_data = json.loads(request_body)
            job_id = callback_data.get("job_id")
            status = callback_data.get("status")
            result = callback_data.get("result")

            print(f"Job ID: {job_id}")
            print(f"Status: {status}")
            print(f"Result: {result}")

            # Process the callback based on status
            if status == "completed":
                print("Job analysis completed successfully!")
                # Handle successful completion
            elif status == "failed":
                print("Job analysis failed!")
                # Handle failure
            else:
                print(f"Job status: {status}")

        except json.JSONDecodeError:
            print("❌ Invalid JSON in callback payload")

    else:
        print("❌ Callback signature verification failed!")
        print("This callback may not be from your job analysis service.")


def main():
    """Main example function."""
    print("=== Job Analysis Webhook Example ===\n")

    # Example 1: Send webhook request
    print("1. Sending job analysis webhook...")
    response = send_job_analysis_webhook()

    if response and response.status_code == 200:
        print("✅ Webhook sent successfully!\n")
    else:
        print("❌ Failed to send webhook\n")

    # Example 2: Verify callback signature
    print("2. Example callback verification...")

    # Simulate callback data (this would come from the actual callback request)
    callback_payload = {
        "status": "completed",
        "job_id": "example-job-123",
        "result": {
            "job_title": "Software Engineer",
            "company_name": "Example Corp",
            "key_responsibilities": ["Develop software", "Write tests"],
            "required_qualifications": ["Python", "FastAPI"],
            "salary_compensation": "$80,000 - $120,000",
            "location_remote_options": "Remote friendly"
        },
        "message": "Job analysis completed successfully",
        "timestamp": "2025-08-22T10:30:00Z"
    }

    # Convert to JSON string as it would appear in request body
    callback_json = json.dumps(
        callback_payload, separators=(',', ':'), sort_keys=True)

    # Generate signature as the service would
    webhook_secret = "your-webhook-secret-key"
    callback_signature = generate_webhook_signature(
        callback_json, webhook_secret)

    print(f"Callback payload: {callback_json}")
    print(f"Callback signature: {callback_signature}")

    # Verify callback
    example_callback_handler(callback_json, callback_signature)


if __name__ == "__main__":
    main()
