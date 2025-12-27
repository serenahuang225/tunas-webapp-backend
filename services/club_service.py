"""
Service layer for club-related operations.
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
from .serializers import serialize_club, serialize_swimmer


class ClubNotFoundError(Exception):
    """Raised when a club is not found."""
    pass


def get_club_by_code(club_code: str, db: Optional[Database] = None) -> dict:
    """
    Get club information by club code.
    
    Args:
        club_code: Club team code (e.g., 'SCSC')
        db: Optional database instance
        
    Returns:
        Serialized club dictionary
        
    Raises:
        ClubNotFoundError: If club is not found
    """
    if db is None:
        db = get_database()
    
    club = db.find_club(club_code)
    if club is None:
        raise ClubNotFoundError(f"Club not found with code: {club_code}")
    
    return serialize_club(club)


def get_club_swimmers(club_code: str, db: Optional[Database] = None) -> dict:
    """
    Get all swimmers in a club.
    
    Args:
        club_code: Club team code (e.g., 'SCSC')
        db: Optional database instance
        
    Returns:
        Dictionary with club info and list of swimmers
        
    Raises:
        ClubNotFoundError: If club is not found
    """
    if db is None:
        db = get_database()
    
    club = db.find_club(club_code)
    if club is None:
        raise ClubNotFoundError(f"Club not found with code: {club_code}")
    
    swimmers = club.get_swimmers()
    
    # Sort by birthday (same as CLI - newest first)
    swimmers.sort(key=lambda s: s.get_birthday_range()[0], reverse=True)
    
    return {
        "club": serialize_club(club),
        "swimmers": [serialize_swimmer(s) for s in swimmers],
    }


