from fastapi import APIRouter, HTTPException
from app.schemas.job import JobCreate, JobUpdate, JobAnalysisResponse
from app.services.job_analyzer import MultiLLMJobAnalyzer
from app.core.config import settings  # Add this import for settings

router = APIRouter()
job_service = MultiLLMJobAnalyzer(settings.LLM_PROVIDER)

@router.post("/", response_model=JobAnalysisResponse)
async def create_job(job: JobCreate):
    """
    Create a new job entry.
    """
    try:
        return await job_service.create_job(job)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{job_id}", response_model=JobAnalysisResponse)
async def get_job(job_id: int):
    """
    Retrieve a job entry by its ID.
    """
    job = await job_service.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job

@router.put("/{job_id}", response_model=JobAnalysisResponse)
async def update_job(job_id: int, job: JobUpdate):
    """
    Update an existing job entry.
    """
    updated_job = await job_service.update_job(job_id, job)
    if not updated_job:
        raise HTTPException(status_code=404, detail="Job not found")
    return updated_job

@router.delete("/{job_id}", response_model=dict)
async def delete_job(job_id: int):
    """
    Delete a job entry by its ID.
    """
    success = await job_service.delete_job(job_id)
    if not success:
        raise HTTPException(status_code=404, detail="Job not found")
    return {"detail": "Job deleted successfully"}