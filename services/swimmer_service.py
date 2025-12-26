"""
Service layer for swimmer-related operations.
"""
from typing import List, Optional
import datetime

import sys
import os

# Add tunas package to Python path
# The tunas code uses relative imports (e.g., "import database"), so we need to add
# tunas/tunas/ directly to sys.path so these imports resolve correctly
_tunas_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../tunas/tunas"))
if _tunas_dir not in sys.path:
    sys.path.insert(0, _tunas_dir)

from database import Database, swim

from .database_service import get_database
from .serializers import serialize_swimmer, serialize_meet_result


class SwimmerNotFoundError(Exception):
    """Raised when a swimmer is not found."""
    pass


def get_swimmer_by_id(swimmer_id: str, db: Optional[Database] = None) -> dict:
    """
    Get swimmer information by USA Swimming ID (long format, 14 characters).
    
    Args:
        swimmer_id: USA Swimming ID (14 characters)
        db: Optional database instance (uses singleton if not provided)
        
    Returns:
        Serialized swimmer dictionary
        
    Raises:
        SwimmerNotFoundError: If swimmer is not found
    """
    if db is None:
        db = get_database()
    
    swimmer = db.find_swimmer_with_long_id(swimmer_id)
    if swimmer is None:
        raise SwimmerNotFoundError(f"Swimmer not found with ID: {swimmer_id}")
    
    return serialize_swimmer(swimmer)


def get_swimmer_best_times(swimmer_id: str, db: Optional[Database] = None) -> dict:
    """
    Get swimmer's best times for each event.
    
    Args:
        swimmer_id: USA Swimming ID (14 characters)
        db: Optional database instance
        
    Returns:
        Dictionary with swimmer info and best times list
    """
    if db is None:
        db = get_database()
    
    swimmer = db.find_swimmer_with_long_id(swimmer_id)
    if swimmer is None:
        raise SwimmerNotFoundError(f"Swimmer not found with ID: {swimmer_id}")
    
    from database import dutil
    
    best_times = []
    for event in dutil.Event:
        best_mr = swimmer.get_best_meet_result(event)
        if best_mr is not None:
            best_times.append(serialize_meet_result(best_mr))
    
    return {
        "swimmer": serialize_swimmer(swimmer),
        "best_times": best_times,
    }


def get_swimmer_time_history(swimmer_id: str, db: Optional[Database] = None) -> dict:
    """
    Get swimmer's full time history.
    
    Args:
        swimmer_id: USA Swimming ID (14 characters)
        db: Optional database instance
        
    Returns:
        Dictionary with swimmer info and meet results list
    """
    if db is None:
        db = get_database()
    
    swimmer = db.find_swimmer_with_long_id(swimmer_id)
    if swimmer is None:
        raise SwimmerNotFoundError(f"Swimmer not found with ID: {swimmer_id}")
    
    meet_results = swimmer.get_meet_results()
    
    # Sort by event, date, and session (same as CLI)
    meet_results.sort(
        key=lambda mr: (
            mr.get_event(),
            mr.get_date_of_swim(),
            mr.get_session(),
        )
    )
    
    return {
        "swimmer": serialize_swimmer(swimmer),
        "meet_results": [serialize_meet_result(mr) for mr in meet_results],
    }


