"""
Service layer for time standard operations.
"""
from typing import Optional, List, Dict, Any

import sys
import os

# Add tunas package to Python path
# The tunas code uses relative imports (e.g., "import database"), so we need to add
# tunas/tunas/ directly to sys.path so these imports resolve correctly
_tunas_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../tunas/tunas"))
if _tunas_dir not in sys.path:
    sys.path.insert(0, _tunas_dir)

from database import Database, timestandard, dutil
import pandas as pd

from .database_service import get_database


def get_time_standard_df(
    standard_name: str,
    age_group: str,
    db: Optional[Database] = None
) -> Dict[str, Any]:
    """
    Get time standard DataFrame for a given standard and age group.
    
    Args:
        standard_name: Time standard name ('AGC', 'FW', 'SECT', 'FUT', 'JNAT', 'NAT', 'OT')
        age_group: Age group identifier
        db: Optional database instance
        
    Returns:
        Dictionary with time standard data as list of records
    """
    if db is None:
        db = get_database()
    
    time_standard_info = db.get_time_standard_info()
    
    # Map string to enum
    standard_map = {
        'AGC': timestandard.TimeStandard.AGC,
        'FW': timestandard.TimeStandard.FW,
        'SECT': timestandard.TimeStandard.SECT,
        'FUT': timestandard.TimeStandard.FUT,
        'JNAT': timestandard.TimeStandard.JNAT,
        'NAT': timestandard.TimeStandard.NAT,
        'OT': timestandard.TimeStandard.OT,
    }
    
    if standard_name not in standard_map:
        raise ValueError(f"Invalid standard_name: {standard_name}")
    
    standard = standard_map[standard_name]
    
    # Get age groups for this standard
    age_groups = time_standard_info.get_age_groups(standard)
    
    # Find the age group
    age_group_obj = None
    for ag in age_groups:
        if str(ag) == age_group or ag.name == age_group:
            age_group_obj = ag
            break
    
    if age_group_obj is None:
        raise ValueError(f"Invalid age_group: {age_group} for standard {standard_name}")
    
    # Get DataFrame
    df = time_standard_info.get_time_standard_df(standard, age_group_obj)
    
    # Convert DataFrame to list of records
    return {
        "standard": standard_name,
        "age_group": age_group,
        "data": df.to_dict(orient='records'),
    }


def get_database_stats(db: Optional[Database] = None) -> Dict[str, int]:
    """
    Get database statistics.
    
    Args:
        db: Optional database instance
        
    Returns:
        Dictionary with counts
    """
    if db is None:
        db = get_database()
    
    return {
        "num_clubs": len(db.get_clubs()),
        "num_swimmers": len(db.get_swimmers()),
        "num_meets": len(db.get_meets()),
        "num_meet_results": len(db.get_meet_results()),
    }


