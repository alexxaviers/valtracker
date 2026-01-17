import logging
from typing import Dict, List, Any
from collections import Counter, defaultdict
import pandas as pd

logger = logging.getLogger(__name__)


class TacticalInsights:
    """Generate tactical insights using pandas."""
    
    @staticmethod
    def analyze_maps_played(series_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze map pool across series."""
        maps = []
        
        for series in series_data:
            end_state = series.get("end_state", {})
            series_maps = end_state.get("maps", [])
            
            for map_info in series_maps:
                if isinstance(map_info, dict):
                    map_name = map_info.get("name") or map_info.get("map_name")
                elif isinstance(map_info, str):
                    map_name = map_info
                else:
                    map_name = "unknown"
                
                if map_name:
                    maps.append(map_name)
        
        if not maps:
            return {"maps": {}, "total": 0}
        
        df = pd.DataFrame({"map": maps})
        map_counts = df["map"].value_counts().to_dict()
        
        return {
            "maps": map_counts,
            "total": len(maps)
        }
    
    @staticmethod
    def analyze_plant_sites(series_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze spike plant site preference."""
        plants_by_map = defaultdict(list)
        
        for series in series_data:
            events = series.get("events", {})
            spike_plants = events.get("spike_plants", [])
            
            for plant in spike_plants:
                map_name = plant.get("map", "unknown")
                site = plant.get("site", "unknown")
                plants_by_map[map_name].append(site)
        
        result = {}
        for map_name, sites in plants_by_map.items():
            if sites:
                df = pd.DataFrame({"site": sites})
                site_counts = df["site"].value_counts().to_dict()
                total = len(sites)
                site_percentages = {k: round(v / total * 100, 1) for k, v in site_counts.items()}
                
                result[map_name] = {
                    "counts": site_counts,
                    "percentages": site_percentages,
                    "total": total
                }
        
        return result
    
    @staticmethod
    def analyze_attack_site_preference(series_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze overall attack site preference (similar to plant sites)."""
        # For now, use plant data as proxy for attack preference
        plants_by_map = defaultdict(list)
        
        for series in series_data:
            events = series.get("events", {})
            spike_plants = events.get("spike_plants", [])
            
            for plant in spike_plants:
                map_name = plant.get("map", "unknown")
                site = plant.get("site", "unknown")
                plants_by_map[map_name].append(site)
        
        result = {}
        for map_name, sites in plants_by_map.items():
            if sites:
                df = pd.DataFrame({"site": sites})
                site_counts = df["site"].value_counts().to_dict()
                total = len(sites)
                site_percentages = {k: round(v / total * 100, 1) for k, v in site_counts.items()}
                
                result[map_name] = {
                    "counts": site_counts,
                    "percentages": site_percentages,
                    "total": total
                }
        
        return result
    
    @staticmethod
    def analyze_opening_duels(series_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze opening duel statistics per player."""
        player_stats = defaultdict(lambda: {"first_kills": 0, "first_deaths": 0})
        
        for series in series_data:
            events = series.get("events", {})
            kills = events.get("kills", [])
            
            for kill in kills:
                killer = kill.get("killer")
                victim = kill.get("victim")
                
                # Simplified: track all kills (not just opening duels)
                if killer:
                    player_stats[killer]["first_kills"] += 1
                if victim:
                    player_stats[victim]["first_deaths"] += 1
        
        # Calculate net
        result = {}
        for player, stats in player_stats.items():
            if player and player != "unknown":
                net = stats["first_kills"] - stats["first_deaths"]
                result[player] = {
                    "first_kills": stats["first_kills"],
                    "first_deaths": stats["first_deaths"],
                    "net": net
                }
        
        # Sort by net
        sorted_result = dict(sorted(result.items(), key=lambda x: x[1]["net"], reverse=True))
        
        return sorted_result
    
    @staticmethod
    def analyze_comp_frequency(series_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze agent composition frequency per map."""
        comps_by_map = defaultdict(list)
        
        for series in series_data:
            end_state = series.get("end_state", {})
            series_maps = end_state.get("maps", [])
            comps = end_state.get("comps", {})
            
            # If we have map data and comp data
            if series_maps and comps:
                for map_info in series_maps:
                    map_name = map_info.get("name") if isinstance(map_info, dict) else map_info
                    
                    # For each team comp
                    for team, comp_data in comps.items():
                        agents = comp_data.get("agents", [])
                        if agents:
                            # Create comp signature
                            comp_sig = "+".join(sorted(agents))
                            comps_by_map[map_name].append(comp_sig)
        
        result = {}
        insufficient_data = True
        
        for map_name, comp_list in comps_by_map.items():
            if comp_list:
                insufficient_data = False
                df = pd.DataFrame({"comp": comp_list})
                comp_counts = df["comp"].value_counts().to_dict()
                
                result[map_name] = {
                    "compositions": comp_counts,
                    "total": len(comp_list)
                }
        
        return {
            "by_map": result,
            "insufficient_data": insufficient_data
        }
