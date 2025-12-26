"""
FastAPI routes for database statistics endpoints.
"""
from fastapi import APIRouter, HTTPException

from models import DatabaseStatsResponse
from services.timestandard_service import get_database_stats

router = APIRouter(prefix="/api/stats", tags=["stats"])


@router.get("", response_model=DatabaseStatsResponse)
async def get_stats():
    """
    Get database statistics (counts of clubs, swimmers, meets, and meet results).
    """
    try:
        return get_database_stats()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

