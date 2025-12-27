"""
Serialization functions to convert tunas domain objects to JSON-serializable dicts.
"""
import datetime
from typing import Optional, Dict, Any, List

import sys
import os

def _setup_tunas_path():
    """
    Add tunas package to Python path.
    Tries multiple possible paths to handle different deployment scenarios.
    """
    # List of possible paths to try (relative to this file)
    possible_paths = [
        # Standard development path: backend/services -> project_root/tunas/tunas
        os.path.abspath(os.path.join(os.path.dirname(__file__), "../../tunas/tunas")),
        # Railway/deployment path: might be at root level
        os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../tunas/tunas")),
        # Alternative: if backend is the root
        os.path.abspath(os.path.join(os.path.dirname(__file__), "../tunas/tunas")),
        # Absolute path fallback: try from current working directory
        os.path.join(os.getcwd(), "tunas", "tunas"),
        # Try from project root if we can find it
        os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "tunas", "tunas"),
    ]
    
    for tunas_dir in possible_paths:
        tunas_dir = os.path.abspath(tunas_dir)
        parser_path = os.path.join(tunas_dir, "parser.py")
        if os.path.exists(parser_path):
            if tunas_dir not in sys.path:
                sys.path.insert(0, tunas_dir)
            return tunas_dir
    
    # If we get here, none of the paths worked
    raise ImportError(
        f"Could not find tunas package. Tried paths:\n" +
        "\n".join(f"  - {os.path.abspath(p)}" for p in possible_paths) +
        f"\n\nCurrent working directory: {os.getcwd()}\n" +
        f"Current file location: {os.path.dirname(__file__)}"
    )

# Setup tunas path before importing
_setup_tunas_path()

from database import swim, stime, sdif, dutil, timestandard


def serialize_club(club: Optional[swim.Club]) -> Optional[Dict[str, Any]]:
    """Serialize a Club object to a dictionary."""
    if club is None:
        return None
    
    lsc = club.get_lsc()
    club_code = club.get_team_code()
    
    return {
        "team_code": club_code,
        "lsc": lsc.value if lsc else None,
        "full_name": club.get_full_name(),
        "abbreviated_name": club.get_abbreviated_name(),
        "city": club.get_city(),
        "state": club.get_state().value if club.get_state() else None,
        "country": club.get_country().value if club.get_country() else None,
        "club_code": f"{lsc.value}-{club_code}" if lsc else club_code,
    }


def serialize_swimmer(swimmer: swim.Swimmer) -> Dict[str, Any]:
    """Serialize a Swimmer object to a dictionary."""
    club = swimmer.get_club()
    today = datetime.date.today()
    age_range = swimmer.get_age_range(today)
    birthday_range = swimmer.get_birthday_range()
    
    return {
        "id": swimmer.get_usa_id_long(),
        "id_short": swimmer.get_usa_id_short(),
        "first_name": swimmer.get_first_name(),
        "last_name": swimmer.get_last_name(),
        "full_name": swimmer.get_full_name(),
        "middle_initial": swimmer.get_middle_initial(),
        "preferred_first_name": swimmer.get_preferred_first_name(),
        "sex": swimmer.get_sex().value,
        "birthday": swimmer.get_birthday().isoformat() if swimmer.get_birthday() else None,
        "birthday_range": {
            "min": birthday_range[0].isoformat(),
            "max": birthday_range[1].isoformat(),
        },
        "age_range": {
            "min": age_range[0],
            "max": age_range[1],
        },
        "club": serialize_club(club),
        "citizenship": swimmer.get_citizenship().value if swimmer.get_citizenship() else None,
    }


def serialize_meet(meet: swim.Meet) -> Dict[str, Any]:
    """Serialize a Meet object to a dictionary."""
    return {
        "name": meet.get_name(),
        "city": meet.get_city(),
        "state": meet.get_state().value if meet.get_state() else None,
        "start_date": meet.get_start_date().isoformat(),
        "end_date": meet.get_end_date().isoformat(),
        "course": meet.get_course().value if meet.get_course() else None,
        "meet_type": meet.get_meet_type().value if meet.get_meet_type() else None,
    }


def serialize_meet_result(mr: swim.IndividualMeetResult) -> Dict[str, Any]:
    """Serialize an IndividualMeetResult object to a dictionary."""
    event = mr.get_event()
    
    return {
        "event": str(event),
        "event_distance": event.get_distance(),
        "event_stroke": str(event.get_stroke()),
        "event_course": str(event.get_course()),
        "time": str(mr.get_final_time()),
        "session": mr.get_session().value,
        "date": mr.get_date_of_swim().isoformat(),
        "meet": serialize_meet(mr.get_meet()),
        "heat": mr.get_heat(),
        "lane": mr.get_lane(),
        "rank": mr.get_rank(),
        "points": mr.get_points(),
        "age_class": mr.get_swimmer_age_class(),
        "team_code": mr.get_team_code(),
        "lsc": mr.get_lsc().value if mr.get_lsc() else None,
    }


def serialize_time_standard(time_standard: timestandard.TimeStandard) -> str:
    """Serialize a TimeStandard enum to its string value."""
    return time_standard.value if hasattr(time_standard, 'value') else str(time_standard)


def serialize_relay_swimmer(
    swimmer: swim.Swimmer, 
    leg_event: dutil.Event,
    relay_date: datetime.date
) -> Dict[str, Any]:
    """Serialize a swimmer for relay display."""
    best_mr = swimmer.get_best_meet_result(leg_event)
    age_range = swimmer.get_age_range(relay_date)
    
    result = serialize_swimmer(swimmer)
    result.update({
        "best_time": str(best_mr.get_final_time()) if best_mr else None,
        "age_at_relay": age_range[0] if age_range[0] == age_range[1] else age_range,
    })
    
    return result


def serialize_relay(
    relay: List[swim.Swimmer],
    event: dutil.Event,
    relay_time: Optional[stime.Time],
    time_standards: Optional[List[Any]] = None
) -> Dict[str, Any]:
    """Serialize a relay team."""
    # Import here to avoid circular dependencies
    import relaygen
    
    leg_events = relaygen.get_relay_leg_events(event)
    
    return {
        "event": str(event),
        "distance": event.get_distance(),
        "stroke": str(event.get_stroke()),
        "course": str(event.get_course()),
        "total_time": str(relay_time) if relay_time else None,
        "time_standards": [str(ts) for ts in time_standards] if time_standards else [],
        "swimmers": [
            serialize_swimmer(swimmer) for swimmer in relay
        ] if relay else [],
        "leg_events": [str(le) for le in leg_events],
    }

