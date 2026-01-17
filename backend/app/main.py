import logging
import time
from typing import List, Dict, Any

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import JSONResponse

from app.settings import settings
from app.grid_client import GridClient
from app.parsers import EventParser, EndStateParser
from app.insights import TacticalInsights
from app.report import ReportGenerator
from app.schemas import ScoutRequest, ScoutResponse, HealthResponse

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="VALORANT Scout POC",
    description="Scouting report generator using GRID File Download API",
    version="0.1.0"
)

grid_client = GridClient()


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    return HealthResponse(
        status="healthy",
        message="VALORANT Scout service is operational"
    )


@app.get("/scout/valorant")
async def scout_valorant(
    series_ids: str = Query(None, description="Comma-separated series IDs"),
    team_id: str = Query(None, description="Team ID (not yet implemented)"),
    last_n: int = Query(10, description="Last N series (not yet implemented)")
):
    """
    Generate scouting report for VALORANT.
    
    Supports two modes:
    1. Explicit series IDs: ?series_ids=ID1,ID2,ID3
    2. Team-based lookup (returns 501): ?team_id=TEAM&last_n=10
    """
    
    # Handle team_id mode (not implemented)
    if team_id and not series_ids:
        not_impl = grid_client.get_series_ids_for_team(team_id, last_n)
        raise HTTPException(
            status_code=501,
            detail={
                "error": not_impl["error"],
                "message": not_impl["message"],
                "workaround": not_impl["workaround"]
            }
        )
    
    # Require series_ids
    if not series_ids:
        raise HTTPException(
            status_code=400,
            detail="Must provide series_ids parameter (e.g., ?series_ids=ID1,ID2,ID3)"
        )
    
    # Parse series IDs
    parsed_series_ids = [s.strip() for s in series_ids.split(",")]
    logger.info(f"Generating scout report for {len(parsed_series_ids)} series: {parsed_series_ids}")
    
    # Fetch and parse data for each series
    series_data = []
    
    for series_id in parsed_series_ids:
        try:
            logger.info(f"Processing series: {series_id}")
            
            # Rate limit protection
            time.sleep(0.5)
            
            # List files
            logger.debug(f"Listing files for {series_id}")
            files = grid_client.list_files(series_id)
            
            # Download events
            logger.debug(f"Downloading events for {series_id}")
            grid_client.download_events_zip(series_id)
            
            # Download end-state
            logger.debug(f"Downloading end-state for {series_id}")
            grid_client.download_end_state(series_id)
            
            # Parse events
            logger.debug(f"Parsing events for {series_id}")
            events = EventParser.parse_events(series_id)
            
            # Parse end-state
            logger.debug(f"Parsing end-state for {series_id}")
            end_state = EndStateParser.parse_end_state(series_id)
            
            series_data.append({
                "series_id": series_id,
                "events": events,
                "end_state": end_state
            })
            
            logger.info(f"Successfully processed {series_id}")
        
        except Exception as e:
            logger.error(f"Error processing series {series_id}: {e}")
            raise HTTPException(
                status_code=500,
                detail=f"Error processing series {series_id}: {str(e)}"
            )
    
    if not series_data:
        raise HTTPException(
            status_code=400,
            detail="No valid series data could be retrieved"
        )
    
    # Generate insights
    logger.info("Generating tactical insights")
    maps_played = TacticalInsights.analyze_maps_played(series_data)
    attack_site_preference = TacticalInsights.analyze_attack_site_preference(series_data)
    plant_sites = TacticalInsights.analyze_plant_sites(series_data)
    opening_duels = TacticalInsights.analyze_opening_duels(series_data)
    comp_frequency = TacticalInsights.analyze_comp_frequency(series_data)
    
    # Generate markdown report
    logger.info("Generating markdown report")
    markdown_report = ReportGenerator.generate_markdown_report(
        series_ids=parsed_series_ids,
        maps_played=maps_played,
        attack_site_preference=attack_site_preference,
        plant_sites=plant_sites,
        opening_duels=opening_duels,
        comp_frequency=comp_frequency
    )
    
    # Build response
    response = {
        "series_analyzed": parsed_series_ids,
        "maps_played": maps_played,
        "comp_frequency": comp_frequency,
        "attack_site_preference": attack_site_preference,
        "plant_sites": plant_sites,
        "opening_duels": opening_duels,
        "markdown_report": markdown_report
    }
    
    logger.info("Scout report generated successfully")
    return JSONResponse(content=response)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )
