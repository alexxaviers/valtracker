import json
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional
from collections import defaultdict

from app.cache import get_cache_path

logger = logging.getLogger(__name__)


class EventParser:
    """Parse GRID events JSONL files."""
    
    @staticmethod
    def parse_events(series_id: str) -> Dict[str, Any]:
        """
        Parse events from JSONL files in cache.
        Returns structured data for analysis.
        """
        cache_dir = get_cache_path(series_id)
        events_by_round = defaultdict(list)
        spike_plants = []
        kills = []
        schema_preview = {}
        
        # Find all JSONL files
        jsonl_files = list(cache_dir.glob("**/*.jsonl"))
        
        if not jsonl_files:
            logger.warning(f"No JSONL files found in {cache_dir}")
            return {
                "spike_plants": [],
                "kills": [],
                "events_by_round": {},
                "schema_preview": {}
            }
        
        for jsonl_file in jsonl_files:
            try:
                with open(jsonl_file, "r") as f:
                    for line in f:
                        if not line.strip():
                            continue
                        
                        event = json.loads(line)
                        
                        # Capture schema preview
                        if not schema_preview:
                            schema_preview = {
                                "sample_keys": list(event.keys())[:10],
                                "file": str(jsonl_file.name)
                            }
                        
                        # Detect spike plant events
                        if EventParser._is_spike_plant(event):
                            plant = EventParser._extract_plant_info(event)
                            if plant:
                                spike_plants.append(plant)
                        
                        # Detect kill events
                        if EventParser._is_kill(event):
                            kill = EventParser._extract_kill_info(event)
                            if kill:
                                kills.append(kill)
                        
                        # Group by round
                        round_id = event.get("round_id", "unknown")
                        events_by_round[round_id].append(event)
            
            except json.JSONDecodeError as e:
                logger.error(f"JSON parse error in {jsonl_file}: {e}")
            except Exception as e:
                logger.error(f"Error processing {jsonl_file}: {e}")
        
        # Save schema preview
        schema_path = cache_dir / "schema_preview.json"
        with open(schema_path, "w") as f:
            json.dump(schema_preview, f, indent=2)
        
        return {
            "spike_plants": spike_plants,
            "kills": kills,
            "events_by_round": dict(events_by_round),
            "schema_preview": schema_preview
        }
    
    @staticmethod
    def _is_spike_plant(event: dict) -> bool:
        """Check if event is a spike plant."""
        event_type = event.get("event_type", "").lower()
        return "plant" in event_type or event.get("type") == "plant_spike"
    
    @staticmethod
    def _extract_plant_info(event: dict) -> Optional[dict]:
        """Extract relevant plant event info."""
        try:
            return {
                "map": event.get("map") or event.get("map_name") or "unknown",
                "site": event.get("site", "unknown"),
                "round": event.get("round_id"),
                "timestamp": event.get("timestamp"),
                "round_time": event.get("round_time"),
                "raw_event": event
            }
        except Exception as e:
            logger.debug(f"Error extracting plant info: {e}")
            return None
    
    @staticmethod
    def _is_kill(event: dict) -> bool:
        """Check if event is a kill."""
        event_type = event.get("event_type", "").lower()
        return "kill" in event_type or event.get("type") == "kill"
    
    @staticmethod
    def _extract_kill_info(event: dict) -> Optional[dict]:
        """Extract relevant kill event info."""
        try:
            return {
                "killer": event.get("killer") or event.get("killer_name"),
                "victim": event.get("victim") or event.get("victim_name"),
                "round": event.get("round_id"),
                "timestamp": event.get("timestamp"),
                "round_time": event.get("round_time"),
                "raw_event": event
            }
        except Exception as e:
            logger.debug(f"Error extracting kill info: {e}")
            return None


class EndStateParser:
    """Parse GRID end-state JSON file."""
    
    @staticmethod
    def parse_end_state(series_id: str) -> Dict[str, Any]:
        """Parse end-state JSON."""
        cache_dir = get_cache_path(series_id)
        end_state_path = cache_dir / "end_state.json"
        
        if not end_state_path.exists():
            logger.warning(f"No end_state.json found in {cache_dir}")
            return {
                "maps": [],
                "comps": [],
                "players": []
            }
        
        try:
            with open(end_state_path, "r") as f:
                data = json.load(f)
            
            maps = []
            comps = defaultdict(lambda: {"agents": []})
            players = []
            
            # Extract maps (defensive parsing)
            if "maps" in data:
                maps = data.get("maps", [])
            
            # Extract player agents (if present)
            if "players" in data:
                for player in data.get("players", []):
                    player_info = {
                        "name": player.get("name", "unknown"),
                        "agent": player.get("agent") or player.get("selected_agent", "unknown"),
                        "team": player.get("team", "unknown")
                    }
                    players.append(player_info)
                    
                    # Track comps by team
                    team = player.get("team", "unknown")
                    agent = player.get("agent") or player.get("selected_agent")
                    if agent:
                        comps[team]["agents"].append(agent)
            
            return {
                "maps": maps,
                "comps": dict(comps),
                "players": players,
                "raw_data": data
            }
        
        except json.JSONDecodeError as e:
            logger.error(f"JSON parse error in end_state.json: {e}")
            return {"maps": [], "comps": [], "players": []}
        except Exception as e:
            logger.error(f"Error parsing end_state.json: {e}")
            return {"maps": [], "comps": [], "players": []}
