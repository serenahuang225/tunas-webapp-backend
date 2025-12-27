"""
Database service for initializing and accessing the tunas database.
"""
import os
import sys
from typing import Optional

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
_tunas_dir = _setup_tunas_path()

import parser
from database import Database

# Singleton database instance
_db: Optional[Database] = None


def _find_meet_data_path() -> str:
    """
    Find the meet data directory by trying multiple possible paths.
    Uses the tunas directory location to find the data directory.
    """
    # List of possible paths to try
    possible_paths = [
        # Standard: tunas/tunas -> tunas/data/meetData
        os.path.join(os.path.dirname(_tunas_dir), "data", "meetData"),
        # Alternative: from project root
        os.path.join(os.path.dirname(os.path.dirname(_tunas_dir)), "tunas", "data", "meetData"),
        # From backend/services -> project_root/tunas/data/meetData
        os.path.abspath(os.path.join(os.path.dirname(__file__), "../../tunas/data/meetData")),
        # Railway/deployment path
        os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../tunas/data/meetData")),
        # From current working directory
        os.path.join(os.getcwd(), "tunas", "data", "meetData"),
    ]
    
    for meet_data_path in possible_paths:
        meet_data_path = os.path.abspath(meet_data_path)
        if os.path.exists(meet_data_path):
            return meet_data_path
    
    # If we get here, none of the paths worked
    raise FileNotFoundError(
        f"Meet data directory not found. Tried paths:\n" +
        "\n".join(f"  - {os.path.abspath(p)}" for p in possible_paths) +
        f"\n\nCurrent working directory: {os.getcwd()}\n" +
        f"Tunas package location: {_tunas_dir}"
    )


def get_database() -> Database:
    """
    Get or initialize the database singleton.
    Database is loaded on first access.
    """
    global _db
    if _db is None:
        meet_data_path = _find_meet_data_path()
        _db = parser.read_cl2(meet_data_path)
    return _db


def reset_database() -> None:
    """
    Reset the database singleton (useful for testing or reloading data).
    """
    global _db
    _db = None


