# Tunas API Backend

FastAPI backend that wraps the existing Tunas CLI functionality to provide a REST API for analyzing USA Swimming meet results.

## Installation

1. Install dependencies:
```bash
cd backend
pip install -r requirements.txt
```

2. Ensure the tunas data directory exists at `tunas/data/meetData/` with CL2 files.

## Running the Server

### Development Mode

```bash
cd backend
python main.py
```

The server will start on `http://localhost:8000`

### Using Uvicorn Directly

```bash
cd backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## API Documentation

Once the server is running, visit:
- **Interactive API docs (Swagger UI)**: http://localhost:8000/docs
- **Alternative docs (ReDoc)**: http://localhost:8000/redoc

## API Endpoints

### Health Check

```bash
curl http://localhost:8000/health
```

### Database Statistics

```bash
curl http://localhost:8000/api/stats
```

**Response:**
```json
{
  "num_clubs": 1234,
  "num_swimmers": 56789,
  "num_meets": 456,
  "num_meet_results": 123456
}
```

### Swimmer Information

#### Get Swimmer by ID

```bash
curl http://localhost:8000/api/swimmers/49AC52F6961843
```

**Response:**
```json
{
  "id": "49AC52F6961843",
  "id_short": "123456789012",
  "first_name": "Irene",
  "last_name": "Zhong",
  "full_name": "Irene Zhong",
  "middle_initial": null,
  "preferred_first_name": null,
  "sex": "F",
  "birthday": "2014-05-15",
  "birthday_range": {
    "min": "2014-05-15",
    "max": "2014-05-15"
  },
  "age_range": {
    "min": 10,
    "max": 10
  },
  "club": {
    "team_code": "SCSC",
    "lsc": "PC",
    "full_name": "Santa Clara Swim Club",
    "abbreviated_name": null,
    "city": "Santa Clara",
    "state": "CA",
    "country": "USA",
    "club_code": "PC-SCSC"
  },
  "citizenship": "USA"
}
```

#### Get Swimmer Best Times

```bash
curl http://localhost:8000/api/swimmers/49AC52F6961843/best-times
```

**Response:**
```json
{
  "swimmer": { ... },
  "best_times": [
    {
      "event": "FREE_50_SCY",
      "event_distance": 50,
      "event_stroke": "FREESTYLE",
      "event_course": "SCY",
      "time": "0:25.43",
      "session": "FINALS",
      "date": "2024-03-15",
      "meet": {
        "name": "2024 Spring Championships",
        "city": "Santa Clara",
        "state": "CA",
        "start_date": "2024-03-14",
        "end_date": "2024-03-17",
        "course": "SCY",
        "meet_type": null
      },
      "heat": 1,
      "lane": 4,
      "rank": 1,
      "points": 20.0,
      "age_class": "10",
      "team_code": "SCSC",
      "lsc": "PC"
    }
  ]
}
```

#### Get Swimmer Full Time History

```bash
curl http://localhost:8000/api/swimmers/49AC52F6961843/times
```

### Club Information

#### Get Club Information

```bash
curl http://localhost:8000/api/clubs/SCSC
```

**Response:**
```json
{
  "team_code": "SCSC",
  "lsc": "PC",
  "full_name": "Santa Clara Swim Club",
  "abbreviated_name": "SCSC",
  "city": "Santa Clara",
  "state": "CA",
  "country": "USA",
  "club_code": "PC-SCSC"
}
```

#### Get Club Roster (All Swimmers)

```bash
curl http://localhost:8000/api/clubs/SCSC/swimmers
```

**Response:**
```json
{
  "club": { ... },
  "swimmers": [
    {
      "id": "49AC52F6961843",
      "first_name": "Irene",
      "last_name": "Zhong",
      "full_name": "Irene Zhong",
      ...
    },
    ...
  ]
}
```

### Relay Generation

Generate optimal relay teams based on swimmer best times.

```bash
curl -X POST http://localhost:8000/api/relays/generate \
  -H "Content-Type: application/json" \
  -d '{
    "club_code": "SCSC",
    "event_type": "4x50_MEDLEY",
    "age_range": [1, 10],
    "sex": "F",
    "course": "LCM",
    "relay_date": "2025-06-08",
    "num_relays": 2,
    "excluded_swimmer_ids": []
  }'
```

**Request Parameters:**
- `club_code` (string, required): Club team code (e.g., "SCSC")
- `event_type` (string, required): One of:
  - `"4x50_FREE"` - 4x50 Freestyle Relay
  - `"4x50_MEDLEY"` - 4x50 Medley Relay
  - `"4x100_FREE"` - 4x100 Freestyle Relay
  - `"4x100_MEDLEY"` - 4x100 Medley Relay
  - `"4x200_FREE"` - 4x200 Freestyle Relay
- `age_range` (tuple[int, int], required): Age range as [min_age, max_age]
- `sex` (string, required): `"F"` (Female), `"M"` (Male), or `"X"` (Mixed)
- `course` (string, required): `"SCY"`, `"SCM"`, or `"LCM"`
- `relay_date` (string, required): Date for age calculations (YYYY-MM-DD)
- `num_relays` (integer, optional): Number of relay teams to generate (default: 1)
- `excluded_swimmer_ids` (array[string], optional): List of swimmer IDs to exclude

**Response:**
```json
{
  "relays": [
    {
      "event": "4x50_MEDLEY_LCM",
      "distance": 200,
      "stroke": "MEDLEY_RELAY",
      "course": "LCM",
      "total_time": "2:31.43",
      "time_standards": ["AAAA"],
      "swimmers": [
        {
          "id": "49AC52F6961843",
          "first_name": "Irene",
          "last_name": "Zhong",
          ...
        },
        ...
      ],
      "leg_events": ["BACK_50_LCM", "BREAST_50_LCM", "FLY_50_LCM", "FREE_50_LCM"]
    },
    {
      "event": "4x50_MEDLEY_LCM",
      "distance": 200,
      "stroke": "MEDLEY_RELAY",
      "course": "LCM",
      "total_time": "2:50.72",
      "time_standards": ["AA"],
      "swimmers": [...]
    }
  ],
  "settings": {
    "club_code": "SCSC",
    "age_range": [1, 10],
    "sex": "F",
    "course": "LCM",
    "relay_date": "2025-06-08",
    "num_relays": 2,
    "event_type": "4x50_MEDLEY"
  }
}
```

## Example curl Requests

### Complete Examples

```bash
# Health check
curl http://localhost:8000/health

# Database statistics
curl http://localhost:8000/api/stats

# Get swimmer information (replace ID with actual swimmer ID)
curl http://localhost:8000/api/swimmers/49AC52F6961843

# Get swimmer best times
curl http://localhost:8000/api/swimmers/49AC52F6961843/best-times

# Get swimmer full time history
curl http://localhost:8000/api/swimmers/49AC52F6961843/times

# Get club information
curl http://localhost:8000/api/clubs/SCSC

# Get club roster
curl http://localhost:8000/api/clubs/SCSC/swimmers

# Generate relay teams
curl -X POST http://localhost:8000/api/relays/generate \
  -H "Content-Type: application/json" \
  -d '{
    "club_code": "SCSC",
    "event_type": "4x50_MEDLEY",
    "age_range": [1, 10],
    "sex": "F",
    "course": "LCM",
    "relay_date": "2025-06-08",
    "num_relays": 2
  }'

# Generate relay with excluded swimmers
curl -X POST http://localhost:8000/api/relays/generate \
  -H "Content-Type: application/json" \
  -d '{
    "club_code": "SCSC",
    "event_type": "4x100_FREE",
    "age_range": [11, 12],
    "sex": "M",
    "course": "SCY",
    "relay_date": "2025-01-15",
    "num_relays": 1,
    "excluded_swimmer_ids": ["12345678901234"]
  }'
```

## Error Handling

The API returns appropriate HTTP status codes:

- `200 OK` - Successful request
- `400 Bad Request` - Invalid request parameters
- `404 Not Found` - Resource not found (e.g., swimmer or club)
- `500 Internal Server Error` - Server error

Example error response:
```json
{
  "detail": "Swimmer not found with ID: 12345678901234"
}
```

## Architecture

The backend is structured as follows:

```
backend/
├── main.py                    # FastAPI application entry point
├── models.py                  # Pydantic models for request/response
├── services/                  # Business logic service layer
│   ├── database_service.py   # Database initialization and singleton
│   ├── serializers.py        # Domain object serialization
│   ├── swimmer_service.py    # Swimmer-related operations
│   ├── club_service.py       # Club-related operations
│   ├── relay_service.py      # Relay generation operations
│   └── timestandard_service.py # Time standard operations
└── api/                       # FastAPI route handlers
    ├── swimmer_routes.py     # Swimmer endpoints
    ├── club_routes.py        # Club endpoints
    ├── relay_routes.py       # Relay endpoints
    └── stats_routes.py       # Statistics endpoints
```

The backend wraps the existing `tunas/` package without modifying its core logic, allowing both the CLI and API to share the same business logic.


