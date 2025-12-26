"""
FastAPI routes for relay generation endpoints.
"""
from fastapi import APIRouter, HTTPException

from models import RelayGenerationRequest, RelayGenerationResponse
from services import generate_relays, RelayGenerationError
import datetime

router = APIRouter(prefix="/api/relays", tags=["relays"])


@router.post("/generate", response_model=RelayGenerationResponse)
async def generate_relay_teams(request: RelayGenerationRequest):
    """
    Generate optimal relay teams based on swimmer best times.
    
    **Request body:**
    - **club_code**: Club team code (e.g., 'SCSC')
    - **event_type**: One of '4x50_FREE', '4x50_MEDLEY', '4x100_FREE', '4x100_MEDLEY', '4x200_FREE'
    - **age_range**: Tuple of (min_age, max_age)
    - **sex**: 'F' (Female), 'M' (Male), or 'X' (Mixed)
    - **course**: 'SCY', 'SCM', or 'LCM'
    - **relay_date**: Date for age calculations (YYYY-MM-DD)
    - **num_relays**: Number of relay teams to generate (default: 1)
    - **excluded_swimmer_ids**: Optional list of swimmer IDs to exclude
    """
    try:
        # Convert relay_date string to date object if needed
        if isinstance(request.relay_date, str):
            relay_date = datetime.date.fromisoformat(request.relay_date)
        else:
            relay_date = request.relay_date
        
        result = generate_relays(
            club_code=request.club_code.upper(),
            event_type=request.event_type,
            age_range=request.age_range,
            sex=request.sex,
            course=request.course,
            relay_date=relay_date,
            num_relays=request.num_relays,
            excluded_swimmer_ids=request.excluded_swimmer_ids,
        )
        return result
    except RelayGenerationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid input: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

