import json
import re
from fastapi import HTTPException
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
