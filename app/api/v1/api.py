"""
API v1 router configuration.
Aggregates all endpoint routers and configures API versioning.
"""

from fastapi import APIRouter
from app.api.v1.endpoints import webhooks

# Main API router for version 1
api_router = APIRouter()

# Include endpoint routers with prefixes and tags
api_router.include_router(
    webhooks.router,
    prefix="/webhooks",
    tags=["webhooks"]
)

# api_router.include_router(
#     jobs.router,
#     prefix="/jobs",
#     tags=["jobs"]
# )
