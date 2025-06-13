"""
FastAPI dependency injection utilities.
Provides reusable dependencies for endpoints.
"""
from fastapi import Depends, HTTPException
# from sqlalchemy.orm import Session
# from app.core.security import get_current_user
from app.models.job import Job
from app.schemas.job import JobCreate, JobUpdate
from app.utils.logging import logger
from app.services.llm_service import LLMProviderFactory
from app.core.config import settings


# def get_db():
#     # Dependency to get the database session
#     db = SessionLocal()  # Assuming SessionLocal is defined in your database setup
#     try:
#         yield db
#     finally:
#         db.close()


# def get_job(job_id: int, db: Session = Depends(get_db)):
#     # Dependency to get a job by ID
#     job = db.query(Job).filter(Job.id == job_id).first()
#     if job is None:
#         logger.error(f"Job with id {job_id} not found.")
#         raise HTTPException(status_code=404, detail="Job not found")
#     return job


# def get_current_active_user(current_user: str = Depends(get_current_user)):
#     # Dependency to get the current active user
#     if not current_user.is_active:
#         logger.warning("Inactive user attempted to access a resource.")
#         raise HTTPException(status_code=400, detail="Inactive user")
#     return current_user


def get_llm_service() -> LLMProviderFactory:
    """
    Dependency to provide LLM service instance.

    Returns:
        LLMProviderFactory: Configured LLM service instance

    Raises:
        HTTPException: If LLM service cannot be initialized
    """
    try:
        return LLMProviderFactory(
            provider=settings.LLM_PROVIDER,
            api_key=_get_api_key_for_provider(settings.LLM_PROVIDER),
            model_name=settings.DEFAULT_MODEL
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to initialize LLM service: {str(e)}"
        )


def _get_api_key_for_provider(provider: str) -> str:
    """Get API key for specified LLM provider."""
    api_key_map = {
        "openai": settings.OPENAI_API_KEY,
        "gemini": settings.GEMINI_API_KEY,
        "anthropic": settings.ANTHROPIC_API_KEY
    }

    api_key = api_key_map.get(provider.lower())
    if not api_key:
        raise ValueError(f"API key not configured for provider: {provider}")

    return api_key
