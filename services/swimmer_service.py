"""
Service layer for swimmer-related operations.
"""
from typing import List, Optional
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


