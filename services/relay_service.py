"""
Service layer for relay generation operations.
"""
from typing import List, Optional, Dict, Any
import datetime

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

from database import Database, swim, sdif, dutil, timestandard
import relaygen

from .database_service import get_database
from .serializers import serialize_relay


class RelayGenerationError(Exception):
    """Raised when relay generation fails."""
    pass


def generate_relays(
    club_code: str,
    event_type: str,
    age_range: tuple[int, int],
    sex: str,
    course: str,
    relay_date: datetime.date,
    num_relays: int = 2,
    excluded_swimmer_ids: Optional[List[str]] = None,
    db: Optional[Database] = None,
) -> Dict[str, Any]:
    """
    Generate optimal relay teams.
    
    Args:
        club_code: Club team code
        event_type: One of '4x50_FREE', '4x50_MEDLEY', '4x100_FREE', '4x100_MEDLEY', '4x200_FREE'
        age_range: Tuple of (min_age, max_age)
        sex: 'F' (Female), 'M' (Male), or 'X' (Mixed)
        course: 'SCY', 'SCM', or 'LCM'
        relay_date: Date for age calculations
        num_relays: Number of relay teams to generate
        excluded_swimmer_ids: Optional list of swimmer IDs to exclude
        db: Optional database instance
        
    Returns:
        Dictionary with relays and settings
    """
    if db is None:
        db = get_database()
    
    # Find club
    club = db.find_club(club_code)
    if club is None:
        raise RelayGenerationError(f"Club not found with code: {club_code}")
    
    # Map string inputs to enums
    sex_map = {
        'F': sdif.Sex.FEMALE,
        'M': sdif.Sex.MALE,
        'X': sdif.Sex.MIXED,
    }
    course_map = {
        'SCY': sdif.Course.SCY,
        'SCM': sdif.Course.SCM,
        'LCM': sdif.Course.LCM,
    }
    
    if sex not in sex_map:
        raise RelayGenerationError(f"Invalid sex: {sex}. Must be 'F', 'M', or 'X'")
    if course not in course_map:
        raise RelayGenerationError(f"Invalid course: {course}. Must be 'SCY', 'SCM', or 'LCM'")
    
    # Map event type to distance and stroke
    event_map = {
        '4x50_FREE': (200, sdif.Stroke.FREESTYLE_RELAY),
        '4x50_MEDLEY': (200, sdif.Stroke.MEDLEY_RELAY),
        '4x100_FREE': (400, sdif.Stroke.FREESTYLE_RELAY),
        '4x100_MEDLEY': (400, sdif.Stroke.MEDLEY_RELAY),
        '4x200_FREE': (800, sdif.Stroke.FREESTYLE_RELAY),
    }
    
    if event_type not in event_map:
        raise RelayGenerationError(
            f"Invalid event_type: {event_type}. Must be one of {list(event_map.keys())}"
        )
    
    distance, stroke_enum = event_map[event_type]
    
    # Find the matching Event enum member
    event = None
    for e in dutil.Event:
        if (e.get_distance() == distance and 
            e.get_stroke() == stroke_enum and 
            e.get_course() == course_map[course]):
            event = e
            break
    
    if event is None:
        raise RelayGenerationError(
            f"Could not find Event for {event_type} on {course} course"
        )
    
    # Create relay generator
    generator = relaygen.RelayGenerator(
        db=db,
        club=club,
        relay_date=relay_date,
        num_relays=num_relays,
        sex=sex_map[sex],
        course=course_map[course],
        age_range=age_range,
    )
    
    # Exclude swimmers if provided
    if excluded_swimmer_ids:
        invalid_ids = []
        for swimmer_id in excluded_swimmer_ids:
            # Try long ID first (14 characters), then short ID (12 characters)
            excluded_swimmer = None
            if len(swimmer_id) == 14:
                excluded_swimmer = club.find_swimmer_with_long_id(swimmer_id)
            elif len(swimmer_id) == 12:
                excluded_swimmer = club.find_swimmer_with_short_id(swimmer_id)
            else:
                invalid_ids.append(swimmer_id)
                continue
            
            if excluded_swimmer:
                generator.exclude_swimmer(excluded_swimmer)
            else:
                invalid_ids.append(swimmer_id)
        
        if invalid_ids:
            raise RelayGenerationError(
                f"The following swimmer IDs are not valid for club '{club_code}': {', '.join(invalid_ids)}"
            )
    
    # Generate relays
    generated_relays = generator.generate_relays(event)
    
    # Calculate relay times and time standards
    time_standard_info = db.get_time_standard_info()
    
    serialized_relays = []
    for relay in generated_relays:
        if not relay:
            serialized_relays.append(serialize_relay(relay, event, None))
            continue
        
        # Calculate relay time
        relay_time = relaygen.get_relay_time(relay, event)
        
        # Get time standards
        min_age = age_range[0]
        sex_enum = sex_map[sex]
        standards = time_standard_info.get_qualified_standards(
            relay_time,
            event,
            min_age,
            sex_enum,
        )
        
        serialized_relays.append(serialize_relay(relay, event, relay_time, standards))
    
    return {
        "relays": serialized_relays,
        "settings": {
            "club_code": club_code,
            "age_range": age_range,
            "sex": sex,
            "course": course,
            "relay_date": relay_date.isoformat(),
            "num_relays": num_relays,
            "event_type": event_type,
        },
    }

