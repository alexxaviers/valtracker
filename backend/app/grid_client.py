import httpx
import zipfile
import json
import time
import logging
from pathlib import Path
from typing import Optional

from app.settings import settings
from app.cache import get_cache_path, ensure_cache_dir

logger = logging.getLogger(__name__)


class GridClient:
    """Client for interacting with GRID File Download API."""
    
    def __init__(self):
        self.base_url = settings.grid_file_api_base_url
        self.api_key = settings.grid_api_key
        self.headers = {
            "x-api-key": self.api_key,
        }
    
    def list_files(self, series_id: str) -> dict:
        """List available files for a series."""
        url = f"{self.base_url}/list/{series_id}"
        headers = {**self.headers, "Accept": "application/json"}
        
        try:
            with httpx.Client() as client:
                response = client.get(url, headers=headers, timeout=30)
                if response.status_code == 401:
                    raise Exception("Unauthorized: Check your GRID_API_KEY")
                if response.status_code == 403:
                    raise Exception("Forbidden: Check your API permissions")
                response.raise_for_status()
                return response.json()
        except httpx.HTTPError as e:
            logger.error(f"Failed to list files for {series_id}: {e}")
            raise
    
    def download_events_zip(self, series_id: str) -> Optional[Path]:
        """Download and extract events JSONL files."""
        url = f"{self.base_url}/events/grid/series/{series_id}"
        headers = {**self.headers, "Accept": "application/zip"}
        
        cache_dir = get_cache_path(series_id)
        ensure_cache_dir(cache_dir)
        
        zip_path = cache_dir / "events.zip"
        
        try:
            with httpx.Client() as client:
                response = client.get(url, headers=headers, timeout=60)
                if response.status_code == 401:
                    raise Exception("Unauthorized: Check your GRID_API_KEY")
                if response.status_code == 403:
                    raise Exception("Forbidden: Check your API permissions")
                response.raise_for_status()
                
                # Save ZIP
                with open(zip_path, "wb") as f:
                    f.write(response.content)
                
                # Extract JSONL files
                with zipfile.ZipFile(zip_path, "r") as z:
                    z.extractall(cache_dir)
                
                logger.info(f"Downloaded and extracted events for {series_id}")
                return cache_dir
        
        except httpx.HTTPError as e:
            logger.error(f"Failed to download events for {series_id}: {e}")
            raise
    
    def download_end_state(self, series_id: str) -> Optional[Path]:
        """Download end-state JSON file."""
        url = f"{self.base_url}/end-state/grid/series/{series_id}"
        headers = {**self.headers, "Accept": "application/json"}
        
        cache_dir = get_cache_path(series_id)
        ensure_cache_dir(cache_dir)
        
        end_state_path = cache_dir / "end_state.json"
        
        try:
            with httpx.Client() as client:
                response = client.get(url, headers=headers, timeout=30)
                if response.status_code == 401:
                    raise Exception("Unauthorized: Check your GRID_API_KEY")
                if response.status_code == 403:
                    raise Exception("Forbidden: Check your API permissions")
                response.raise_for_status()
                
                # Save JSON
                with open(end_state_path, "w") as f:
                    json.dump(response.json(), f, indent=2)
                
                logger.info(f"Downloaded end-state for {series_id}")
                return end_state_path
        
        except httpx.HTTPError as e:
            logger.error(f"Failed to download end-state for {series_id}: {e}")
            raise
    
    def get_series_ids_for_team(self, team_id: str, last_n: int = 10) -> dict:
        """
        Stub method: would fetch series IDs for a team using Central Data Feed GraphQL API.
        
        This requires GraphQL Query API access which is not currently available.
        Once enabled, this method would query the Central Data Feed to retrieve
        the last N series for a given team_id.
        """
        return {
            "error": "Not Implemented",
            "status": 501,
            "message": (
                "Fetching series IDs via team_id + last_n requires access to the "
                "Central Data Feed GraphQL Query API, which is currently unavailable. "
                "Please provide explicit series_ids instead. "
                "Once the Query API is enabled, this endpoint will be implemented."
            ),
            "workaround": "Use GET /scout/valorant?series_ids=ID1,ID2,ID3 instead"
        }
