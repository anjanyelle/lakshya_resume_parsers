from fastapi import APIRouter

from app.api.v1.endpoints import (
    accuracy,
    analytics,
    auth,
    candidates,
    corrections,
    gdpr,
    health,
    jobs,
    parsing,
    taxonomy,
    review,
    search,
    skills,
    upload,
)

api_router = APIRouter()
api_router.include_router(auth.router, tags=["auth"])
api_router.include_router(health.router, tags=["health"])
api_router.include_router(upload.router, tags=["upload"])
api_router.include_router(candidates.router, tags=["candidates"])
api_router.include_router(parsing.router, tags=["parsing"])
api_router.include_router(jobs.router, tags=["jobs"])
api_router.include_router(search.router, tags=["search"])
api_router.include_router(skills.router, tags=["skills"])
api_router.include_router(analytics.router, tags=["analytics"])
api_router.include_router(gdpr.router, tags=["gdpr"])
api_router.include_router(review.router, tags=["review"])
api_router.include_router(taxonomy.router, tags=["taxonomy"])
api_router.include_router(corrections.router, tags=["corrections"])
api_router.include_router(accuracy.router, tags=["accuracy"])