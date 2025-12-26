"""
Service layer for club-related operations.
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


