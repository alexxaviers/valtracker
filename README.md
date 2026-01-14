# VALORANT Scout POC

A proof-of-concept scouting report generator for VALORANT using the GRID File Download API and FastAPI.

## Overview

This service analyzes completed VALORANT series and produces tactical insights for upcoming opponents. It leverages GRID's File Download API to fetch event data and end-state information, then synthesizes that data into actionable intelligence.

## Architecture

```
valorant-scout-poc/
├── app/
│   ├── main.py           # FastAPI application & endpoints
│   ├── settings.py       # Configuration management
│   ├── grid_client.py    # GRID API interactions
│   ├── parsers.py        # Event & end-state parsing
│   ├── insights.py       # Pandas-based tactical analysis
│   ├── report.py         # Markdown report generation
│   ├── cache.py          # Disk caching utilities
│   └── schemas.py        # Pydantic models
├── data/
│   ├── cache/            # Disk cache for GRID files
│   └── mock/
│       └── series_ids.json
├── requirements.txt
├── .env.example
├── README.md
└── LICENSE
```

## Quick Start

### 1. Clone and Setup

```bash
cd valorant-scout-poc
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows
pip install -r requirements.txt
```

### 2. Configure API Key

Copy `.env.example` to `.env` and add your GRID API key:

```bash
cp .env.example .env
# Edit .env with your GRID_API_KEY
```

### 3. Run the Service

```bash
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`.

## API Endpoints

### Health Check

```
GET /health
```

Returns service status.

### Scout Report (by Series IDs)

```
GET /scout/valorant?series_ids=ID1,ID2,ID3
```

**Parameters:**
- `series_ids` (required): Comma-separated GRID series IDs

**Response:**
```json
{
  "series_analyzed": ["ID1", "ID2", "ID3"],
  "maps_played": {
    "maps": {"Bind": 2, "Haven": 1},
    "total": 3
  },
  "comp_frequency": {
    "by_map": {...},
    "insufficient_data": false
  },
  "attack_site_preference": {
    "Bind": {
      "counts": {"A": 5, "B": 3},
      "percentages": {"A": 62.5, "B": 37.5},
      "total": 8
    }
  },
  "plant_sites": {...},
  "opening_duels": {
    "player_name": {
      "first_kills": 10,
      "first_deaths": 5,
      "net": 5
    }
  },
  "markdown_report": "# VALORANT Scouting Report\n..."
}
```

### Scout Report (by Team ID - Not Implemented)

```
GET /scout/valorant?team_id=TEAM&last_n=10
```

Returns **HTTP 501 Not Implemented** with explanation:

```json
{
  "error": "Not Implemented",
  "message": "Fetching series IDs via team_id + last_n requires access to the Central Data Feed GraphQL Query API, which is currently unavailable. Please provide explicit series_ids instead.",
  "workaround": "Use GET /scout/valorant?series_ids=ID1,ID2,ID3 instead"
}
```

## Data Flow

1. **Input:** Series IDs provided by user
2. **Download:** Grid client fetches events ZIP and end-state JSON from GRID API
3. **Cache:** Files cached to `./data/cache/{series_id}/` for reuse
4. **Parse:** Extract events (kills, spike plants) and agent compositions
5. **Analyze:** Pandas-based tactical insights (maps, sites, duels, comps)
6. **Report:** Generate markdown scouting report with tables and TL;DR

## Features

### Tactical Analysis

- **Map Pool:** Track which maps appear most frequently
- **Site Preference:** Analyze spike plant frequency by site (A/B/Other)
- **Opening Duels:** Per-player first-duel statistics (kills/deaths/net)
- **Agent Compositions:** Identify favorite compositions per map
- **Defensive Parsing:** Handle missing/malformed fields gracefully

### Report Generation

- **Markdown Export:** Human-readable tactical summary
- **Tables & Statistics:** Visual breakdown of site preferences and duels
- **TL;DR Section:** Key takeaways for quick briefing

### Caching & Performance

- Disk-based caching under `./data/cache/`
- Avoids redundant API calls for same series
- Rate-limit protection (0.5s delay between requests)

## GRID API Integration

### Authentication

All requests include header:
```
x-api-key: <GRID_API_KEY>
```

### Endpoints Used

| Method | Endpoint | Accept | Purpose |
|--------|----------|--------|---------|
| GET | `/list/{series_id}` | application/json | List available files |
| GET | `/events/grid/series/{series_id}` | application/zip | Download events JSONL |
| GET | `/end-state/grid/series/{series_id}` | application/json | Download end-state data |

### Error Handling

- **401 Unauthorized:** Check your `GRID_API_KEY`
- **403 Forbidden:** Verify API permissions
- **File Status:** Validates files are "ready" before processing

## Design Decisions

### Why Series IDs Instead of Team ID?

The Central Data Feed GraphQL Query API is currently unavailable. Once enabled, the service can be updated to:

```python
# Future implementation (once Query API is available)
def get_series_ids_for_team(team_id: str, last_n: int = 10):
    query = """
    query GetTeamSeries($teamId: String!, $limit: Int!) {
      team(id: $teamId) {
        series(last: $limit) {
          edges { node { id } }
        }
      }
    }
    """
    # Execute GraphQL query...
```

For now, users explicitly provide series IDs, which ensures:
- No dependency on unavailable infrastructure
- Explicit control over which series to analyze
- Clear audit trail of analyzed matchups

### Defensive Parsing Strategy

GRID event schemas may vary. The parser:
- Inspects keys dynamically
- Tolerates missing fields without crashing
- Logs schema samples to `schema_preview.json` for debugging
- Returns empty results gracefully if data unavailable

### Pandas for Insights

Lightweight and efficient:
- Value counting and aggregation
- Group-by operations
- Easy to extend with new analyses

## Development

### Adding New Insights

1. Add analysis method to `insights.py` using pandas
2. Call from `scout_valorant()` endpoint in `main.py`
3. Include in response JSON
4. Add visualization to `report.py` if needed

### Example: Adding Win Rate Analysis

```python
# insights.py
@staticmethod
def analyze_win_rate(series_data: List[Dict[str, Any]]) -> Dict[str, Any]:
    wins = []
    for series in series_data:
        # Parse win data...
        wins.append({...})
    
    df = pd.DataFrame(wins)
    return df.groupby("team")["result"].value_counts().to_dict()

# main.py - add to scout_valorant():
win_rate = TacticalInsights.analyze_win_rate(series_data)
response["win_rate"] = win_rate
```

## Logging

Logs to console with format: `timestamp - module - level - message`

Enabled at INFO level by default. Set environment variable `LOG_LEVEL` to adjust.

## Reliability Notes

- **Rate Limiting:** 0.5s delay between series requests (configurable)
- **Timeouts:** 30s for JSON requests, 60s for ZIP downloads
- **Error Recovery:** Partial failures (e.g., 1 of 3 series) return errors with context
- **Cache Validation:** Detects and handles corrupted cached files

## Future Enhancements

- [ ] Central Data Feed GraphQL integration (once API available)
- [ ] Opposition trend analysis (eco, strat diversity)
- [ ] Player performance benchmarking
- [ ] Real-time match event streaming
- [ ] Comparative analysis (team A vs team B head-to-head)
- [ ] Predictive outcome modeling

## License

MIT License - See [LICENSE](LICENSE) file

## Support

For issues with the service, check:
1. GRID API key validity (`/health` endpoint)
2. Series IDs are correct and available
3. Logs in console output for parsing errors
4. Cached files in `./data/cache/{series_id}/schema_preview.json` for schema issues