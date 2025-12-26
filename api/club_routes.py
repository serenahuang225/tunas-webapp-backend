"""
FastAPI routes for club endpoints.
"""
from fastapi import APIRouter, HTTPException

from models import ClubResponse, ClubSwimmersResponse
from services import (
    get_club_by_code,
    get_club_swimmers,
    ClubNotFoundError,
)

router = APIRouter(prefix="/api/clubs", tags=["clubs"])


@router.get("/{club_code}", response_model=ClubResponse)
async def get_club(club_code: str):
    """
    Get club information by club code.
    
    - **club_code**: Club team code (e.g., 'SCSC')
    """
    try:
        return get_club_by_code(club_code.upper())
    except ClubNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/{club_code}/swimmers", response_model=ClubSwimmersResponse)
async def get_club_swimmers_list(club_code: str):
    """
    Get all swimmers in a club.
    
    - **club_code**: Club team code (e.g., 'SCSC')
    """
    try:
        return get_club_swimmers(club_code.upper())
    except ClubNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

