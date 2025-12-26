"""
FastAPI routes for swimmer endpoints.
"""
from fastapi import APIRouter, HTTPException

from models import SwimmerResponse, SwimmerBestTimesResponse, SwimmerTimeHistoryResponse
from services import (
    get_swimmer_by_id,
    get_swimmer_best_times,
    get_swimmer_time_history,
    SwimmerNotFoundError,
)

router = APIRouter(prefix="/api/swimmers", tags=["swimmers"])


@router.get("/{swimmer_id}", response_model=SwimmerResponse)
async def get_swimmer(swimmer_id: str):
    """
    Get swimmer information by USA Swimming ID.
    
    - **swimmer_id**: USA Swimming ID (14 characters, long format)
    """
    try:
        return get_swimmer_by_id(swimmer_id)
    except SwimmerNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/{swimmer_id}/best-times", response_model=SwimmerBestTimesResponse)
async def get_best_times(swimmer_id: str):
    """
    Get swimmer's best times for each event.
    
    - **swimmer_id**: USA Swimming ID (14 characters, long format)
    """
    try:
        return get_swimmer_best_times(swimmer_id)
    except SwimmerNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/{swimmer_id}/times", response_model=SwimmerTimeHistoryResponse)
async def get_time_history(swimmer_id: str):
    """
    Get swimmer's full time history (all meet results).
    
    - **swimmer_id**: USA Swimming ID (14 characters, long format)
    """
    try:
        return get_swimmer_time_history(swimmer_id)
    except SwimmerNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

