"""
FastAPI application entry point for Tunas web API.
"""
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api import swimmer_routes, club_routes, relay_routes, stats_routes
from services.database_service import get_database


# Initialize FastAPI app
app = FastAPI(
    title="Tunas API",
    description="REST API for analyzing USA Swimming meet results",
    version="1.0.0",
)

# Enable CORS for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(swimmer_routes.router)
app.include_router(club_routes.router)
app.include_router(relay_routes.router)
app.include_router(stats_routes.router)


@app.on_event("startup")
async def startup_event():
    """
    Pre-load database on application startup.
    This ensures the database is ready before handling requests.
    """
    print("Starting Tunas API...")
    print("Loading database (this may take a moment)...")
    try:
        db = get_database()
        print(f"Database loaded successfully!")
        print(f"  - Clubs: {len(db.get_clubs()):,}")
        print(f"  - Swimmers: {len(db.get_swimmers()):,}")
        print(f"  - Meets: {len(db.get_meets()):,}")
        print(f"  - Meet Results: {len(db.get_meet_results()):,}")
    except Exception as e:
        print(f"Error loading database: {e}")
        raise


@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "name": "Tunas API",
        "version": "1.0.0",
        "description": "REST API for analyzing USA Swimming meet results",
        "docs": "/docs",
        "endpoints": {
            "swimmers": "/api/swimmers/{swimmer_id}",
            "clubs": "/api/clubs/{club_code}",
            "relays": "/api/relays/generate",
            "stats": "/api/stats",
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    try:
        db = get_database()
        return {
            "status": "healthy",
            "database": "loaded",
            "clubs": len(db.get_clubs()),
            "swimmers": len(db.get_swimmers()),
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
        }


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,  # Enable auto-reload during development
    )


