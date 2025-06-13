"""
FastAPI application entry point for Job Analysis Webhook Service.
Handles application initialization, middleware setup, and route registration.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1.api import api_router
from app.core.config import settings
from app.utils.logging import setup_logging

# Setup application logging
setup_logging()

# Initialize FastAPI application
app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Job Analysis Webhook Service",
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# Configure CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_HOSTS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(api_router, prefix=settings.API_V1_STR)

@app.get("/")
async def root():
    return {"message": "Welcome to the Job Analysis API"}

# Entry point for the application
# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run("app.main:app", host=settings.HOST, port=settings.PORT, reload=True)