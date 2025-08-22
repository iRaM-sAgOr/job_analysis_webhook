from typing import Optional
from datetime import datetime
import json
import re
import hmac
import hashlib
from fastapi import HTTPException
import httpx
from app.utils.logging import get_logger
from app.core.config import settings

logger = get_logger(__name__)


def post_process_llm_output(llm_output: str):
    """
    Post-process LLM output to extract clean JSON.
    Removes code block markers, extra text, and parses JSON.

    Args:
        llm_output: Raw output from LLM

    Returns:
        dict: Parsed JSON as Python dictionary

    Raises:
        HTTPException: If JSON parsing fails
    """
    try:
        # Remove code block markers (```json, ```, etc.)
        cleaned = re.sub(r'^```(?:json)?|```$', '',
                         llm_output.strip(), flags=re.MULTILINE).strip()

        # Remove any leading/trailing text that might not be JSON
        # Find the first { and last } to extract just the JSON part
        start_idx = cleaned.find('{')
        end_idx = cleaned.rfind('}')

        if start_idx == -1 or end_idx == -1:
            raise ValueError("No valid JSON object found in LLM output")

        json_str = cleaned[start_idx:end_idx + 1]

        # Parse JSON
        return json.loads(json_str)

    except (json.JSONDecodeError, ValueError) as e:
        logger.error(f"Failed to parse LLM output as JSON: {e}")
        logger.error(f"LLM output was: {llm_output}")
        raise HTTPException(
            status_code=500,
            detail=f"LLM did not return valid JSON: {str(e)}"
        )


async def send_webhook_callback(callback_url: str, job_id: str, result: dict, status: str):
    """
    Send analysis results to callback URL with JobAnalysisResponse structure.
    Includes HMAC-SHA256 signature for security verification.
    """
    try:
        # Create payload matching JobAnalysisResponse structure
        payload = {
            "status": status,
            "job_id": job_id,
            "result": result if status == "completed" else None,
            "message": {
                "completed": "Job analysis completed successfully",
                "failed": "Failed to scrape job data",
                "error": "Job analysis failed due to an error"
            }.get(status, "Job analysis processed"),
            "timestamp": datetime.utcnow().isoformat()
        }

        # Convert payload to JSON string for consistent hashing
        payload_json = json.dumps(
            payload, separators=(',', ':'), sort_keys=True)

        # Prepare headers
        headers = {
            "Content-Type": "application/json",
            "User-Agent": f"JobAnalysisWebhook/{settings.VERSION}"
        }

        # Add signature if webhook secret is configured
        if settings.WEBHOOK_SECRET:
            signature = hmac.new(
                settings.WEBHOOK_SECRET.encode('utf-8'),
                payload_json.encode('utf-8'),
                hashlib.sha256
            ).hexdigest()
            headers["X-Webhook-Signature"] = f"sha256={signature}"
            logger.debug(
                f"Added webhook signature for callback to {callback_url}")
        else:
            logger.warning(
                "No WEBHOOK_SECRET configured - callback sent without signature")

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                callback_url,
                data=payload_json,  # Send as raw JSON string to match signature
                headers=headers
            )
            response.raise_for_status()
            logger.info(
                f"Webhook callback sent successfully for job_id: {job_id}")
    except Exception as e:
        logger.error(
            f"Failed to send webhook callback for job_id {job_id}: {str(e)}")


def verify_callback_signature(payload: str, signature: Optional[str] = None, secret: Optional[str] = None) -> bool:
    """
    Verify HMAC-SHA256 signature for callback webhook payloads.

    This utility function can be used by callback receivers to verify
    that the callback payload came from this job analysis service.

    Args:
        payload: Raw JSON payload as string
        signature: Signature from X-Webhook-Signature header (format: "sha256=...")
        secret: Webhook secret key (should match WEBHOOK_SECRET)

    Returns:
        bool: True if signature is valid, False otherwise

    Example usage at callback receiver:
        payload = request.body.decode('utf-8')  # Raw JSON string
        signature = request.headers.get('X-Webhook-Signature')
        if verify_callback_signature(payload, signature, 'your-webhook-secret'):
            # Process callback safely
            data = json.loads(payload)
        else:
            # Reject invalid callback
            return 401
    """
    if not signature or not signature.startswith("sha256=") or not secret:
        return False

    try:
        expected_signature = hmac.new(
            secret.encode('utf-8'),
            payload.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()

        # Extract hash from "sha256=..." format
        received_hash = signature[7:]  # Remove "sha256=" prefix

        return hmac.compare_digest(expected_signature, received_hash)
    except Exception:
        return False
