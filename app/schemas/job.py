"""
Pydantic schemas for job analysis data validation.
Defines request/response models for API endpoints.
"""
from pydantic import BaseModel, Field, field_validator
from typing import Dict, Any, Optional, List
from datetime import datetime


class JobBase(BaseModel):
    title: str
    description: str
    company: str
    location: str
    salary: Optional[float] = None


class JobCreate(JobBase):
    pass


class JobUpdate(JobBase):
    title: Optional[str] = None
    description: Optional[str] = None
    company: Optional[str] = None
    location: Optional[str] = None
    salary: Optional[float] = None


class Job(JobBase):
    id: int

    class Config:
        orm_mode = True


class JobList(BaseModel):
    jobs: List[Job]


class JobAnalysisWebhook(BaseModel):
    """Schema for incoming job analysis webhook data."""

    job_id: str = Field(..., description="Unique job identifier")
    url: str = Field(..., description="URL of the job post to analyze")
    async_processing: bool = Field(
        default=True, description="Enable async processing")
    callback_url: Optional[str] = Field(
        None, description="Callback URL for results")

    @field_validator('job_id')
    def validate_job_id(cls, v):
        if not v or len(v.strip()) == 0:
            raise ValueError('job_id cannot be empty')
        return v.strip()

    @field_validator('url')
    def validate_url(cls, v):
        if not v or not v.startswith("https"):
            raise ValueError('A valid job post URL is required')
        return v

    @field_validator('callback_url')
    def validate_callback_url(cls, v):
        if v is not None:
            if not v or len(v.strip()) == 0:
                raise ValueError('callback_url cannot be empty')
            if not v.strip().startswith("https"):
                raise ValueError('callback_url must be a valid HTTPS URL')
            return v.strip()
        return v


class JobAnalysisResponse(BaseModel):
    """Schema for job analysis response."""

    status: str = Field(..., description="Processing status")
    job_id: str = Field(..., description="Job identifier")
    result: Optional[Dict[str, Any]] = Field(
        None, description="Analysis results")
    message: str = Field(..., description="Status message")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
