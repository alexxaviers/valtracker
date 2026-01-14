from pydantic import BaseModel
from typing import List, Dict, Any, Optional


class ScoutRequest(BaseModel):
    """Request to generate scouting report."""
    series_ids: Optional[str] = None
    team_id: Optional[str] = None
    last_n: Optional[int] = 10


class MapStats(BaseModel):
    """Map statistics."""
    maps: Dict[str, int]
    total: int


class SitePreference(BaseModel):
    """Site preference for a map."""
    counts: Dict[str, int]
    percentages: Dict[str, float]
    total: int


class PlayerDuelStats(BaseModel):
    """Player opening duel statistics."""
    first_kills: int
    first_deaths: int
    net: int


class ScoutResponse(BaseModel):
    """Scout report response."""
    series_analyzed: List[str]
    maps_played: Dict[str, Any]
    comp_frequency: Dict[str, Any]
    attack_site_preference: Dict[str, Any]
    plant_sites: Dict[str, Any]
    opening_duels: Dict[str, PlayerDuelStats]
    markdown_report: str


class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    message: str


class ErrorResponse(BaseModel):
    """Error response."""
    error: str
    status: int
    message: str
