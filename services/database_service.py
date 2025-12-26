"""
Database service for initializing and accessing the tunas database.
"""
import os
import sys
from typing import Optional

# Add tunas package to Python path
# The tunas code uses relative imports (e.g., "import database"), so we need to add
# tunas/tunas/ directly to sys.path so these imports resolve correctly
_tunas_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../tunas/tunas"))
if _tunas_dir not in sys.path:
    sys.path.insert(0, _tunas_dir)

import parser
from database import Database

# Singleton database instance
_db: Optional[Database] = None


def get_database() -> Database:
    """
    Get or initialize the database singleton.
    Database is loaded on first access.
    """
    global _db
    if _db is None:
        # Determine path to meet data
        # From backend/services, go to project root, then to tunas/data/meetData
        current_dir = os.path.dirname(os.path.realpath(__file__))
        project_root = os.path.dirname(os.path.dirname(current_dir))
        meet_data_path = os.path.join(project_root, "tunas", "data", "meetData")
        
        if not os.path.exists(meet_data_path):
            raise FileNotFoundError(
                f"Meet data directory not found at: {meet_data_path}\n"
                f"Please ensure the data directory exists or update the path."
            )
        
        _db = parser.read_cl2(meet_data_path)
    return _db


def reset_database() -> None:
    """
    Reset the database singleton (useful for testing or reloading data).
    """
    global _db
    _db = None


