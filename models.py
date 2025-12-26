"""
Pydantic models for request/response validation.
"""
from typing import Optional, List, Dict, Any
from datetime import date
from pydantic import BaseModel, Field


# Request Models
class RelayGenerationRequest(BaseModel):
    """Request model for relay generation."""
    club_code: str = Field(..., description="Club code (e.g., 'SCSC')")
    age_range: tuple[int, int] = Field(..., description="Age range as (min, max)")
    sex: str = Field(..., description="Sex: 'F' (Female), 'M' (Male), or 'X' (Mixed)")
    course: str = Field(..., description="Course: 'SCY', 'SCM', or 'LCM'")
    relay_date: date = Field(..., description="Date for age calculations")
    num_relays: int = Field(1, ge=1, description="Number of relay teams to generate")
    excluded_swimmer_ids: Optional[List[str]] = Field(None, description="List of swimmer IDs to exclude")
    event_type: str = Field(
        ..., 
        description="Event type: '4x50_FREE', '4x50_MEDLEY', '4x100_FREE', '4x100_MEDLEY', '4x200_FREE'"
    )


# Response Models
class ClubCode(BaseModel):
    """Club code representation."""
    team_code: Optional[str]
    lsc: Optional[str]
    club_code: Optional[str]


class ClubResponse(BaseModel):
    """Club information response."""
    team_code: Optional[str]
    lsc: Optional[str]
    full_name: str
    abbreviated_name: Optional[str]
    city: Optional[str]
    state: Optional[str]
    country: Optional[str]
    club_code: Optional[str]


class AgeRange(BaseModel):
    """Age range representation."""
    min: int
    max: int


class BirthdayRange(BaseModel):
    """Birthday range representation."""
    min: str  # ISO date string
    max: str  # ISO date string


class SwimmerResponse(BaseModel):
    """Swimmer information response."""
    id: Optional[str]
    id_short: Optional[str]
    first_name: str
    last_name: str
    full_name: str
    middle_initial: Optional[str]
    preferred_first_name: Optional[str]
    sex: str
    birthday: Optional[str]  # ISO date string
    birthday_range: BirthdayRange
    age_range: AgeRange
    club: Optional[ClubResponse]
    citizenship: Optional[str]


class MeetResponse(BaseModel):
    """Meet information response."""
    name: str
    city: str
    state: Optional[str]
    start_date: str  # ISO date string
    end_date: str  # ISO date string
    course: Optional[str]
    meet_type: Optional[str]


class MeetResultResponse(BaseModel):
    """Meet result response."""
    event: str
    event_distance: int
    event_stroke: str
    event_course: str
    time: str
    session: str
    date: str  # ISO date string
    meet: MeetResponse
    heat: Optional[int]
    lane: Optional[int]
    rank: Optional[int]
    points: Optional[float]
    age_class: Optional[str]
    team_code: Optional[str]
    lsc: Optional[str]
    time_standards: Optional[List[str]] = None


class SwimmerBestTimesResponse(BaseModel):
    """Swimmer best times response."""
    swimmer: SwimmerResponse
    best_times: List[MeetResultResponse]


class SwimmerTimeHistoryResponse(BaseModel):
    """Swimmer full time history response."""
    swimmer: SwimmerResponse
    meet_results: List[MeetResultResponse]


class ClubSwimmersResponse(BaseModel):
    """Club roster response."""
    club: ClubResponse
    swimmers: List[SwimmerResponse]


class DatabaseStatsResponse(BaseModel):
    """Database statistics response."""
    num_clubs: int
    num_swimmers: int
    num_meets: int
    num_meet_results: int


class RelayResponse(BaseModel):
    """Relay team response."""
    event: str
    distance: int
    stroke: str
    course: str
    total_time: Optional[str]
    time_standards: List[str]
    swimmers: List[SwimmerResponse]
    leg_events: List[str]


class RelayGenerationResponse(BaseModel):
    """Relay generation response."""
    relays: List[RelayResponse]
    settings: Dict[str, Any]


class ErrorResponse(BaseModel):
    """Error response."""
    detail: str
    error: Optional[str] = None


