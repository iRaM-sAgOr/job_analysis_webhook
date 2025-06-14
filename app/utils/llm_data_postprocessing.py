from datetime import datetime
import json
import re
from fastapi import HTTPException
import httpx
from app.utils.logging import get_logger

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
    """Send analysis results to callback URL with JobAnalysisResponse structure"""
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

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(callback_url, json=payload)
            response.raise_for_status()
            logger.info(f"Webhook sent successfully for job_id: {job_id}")
    except Exception as e:
        logger.error(f"Failed to send webhook for job_id {job_id}: {str(e)}")
