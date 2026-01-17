from typing import Dict, List, Any
from datetime import datetime


class ReportGenerator:
    """Generate markdown scouting reports."""
    
    @staticmethod
    def generate_markdown_report(
        series_ids: List[str],
        maps_played: Dict[str, Any],
        attack_site_preference: Dict[str, Any],
        plant_sites: Dict[str, Any],
        opening_duels: Dict[str, Any],
        comp_frequency: Dict[str, Any]
    ) -> str:
        """Generate comprehensive markdown scouting report."""
        
        report_lines = [
            "# VALORANT Scouting Report",
            f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}",
            f"**Series Analyzed:** {', '.join(series_ids)}",
            "",
        ]
        
        # Map Pool
        report_lines.extend(ReportGenerator._section_map_pool(maps_played))
        
        # Attack Site Preference
        report_lines.extend(ReportGenerator._section_attack_sites(attack_site_preference))
        
        # Plant Sites (detailed)
        report_lines.extend(ReportGenerator._section_plant_sites(plant_sites))
        
        # Opening Duels
        report_lines.extend(ReportGenerator._section_opening_duels(opening_duels))
        
        # Agent Compositions
        report_lines.extend(ReportGenerator._section_comps(comp_frequency))
        
        # Summary
        report_lines.extend(ReportGenerator._section_summary(
            maps_played,
            attack_site_preference,
            opening_duels
        ))
        
        return "\n".join(report_lines)
    
    @staticmethod
    def _section_map_pool(maps_played: Dict[str, Any]) -> List[str]:
        """Generate map pool section."""
        lines = [
            "## Map Pool",
            ""
        ]
        
        maps = maps_played.get("maps", {})
        if not maps:
            lines.append("*No map data available*")
            return lines
        
        lines.append("| Map | Appearances |")
        lines.append("|-----|-------------|")
        
        for map_name, count in sorted(maps.items(), key=lambda x: x[1], reverse=True):
            lines.append(f"| {map_name} | {count} |")
        
        lines.append("")
        return lines
    
    @staticmethod
    def _section_attack_sites(attack_site_preference: Dict[str, Any]) -> List[str]:
        """Generate attack site preference section."""
        lines = [
            "## Attack Site Preference",
            ""
        ]
        
        if not attack_site_preference:
            lines.append("*No site preference data available*")
            lines.append("")
            return lines
        
        for map_name, data in sorted(attack_site_preference.items()):
            lines.append(f"### {map_name}")
            lines.append("")
            lines.append("| Site | Count | Percentage |")
            lines.append("|------|-------|-----------|")
            
            counts = data.get("counts", {})
            percentages = data.get("percentages", {})
            
            for site, count in sorted(counts.items(), key=lambda x: x[1], reverse=True):
                pct = percentages.get(site, 0)
                lines.append(f"| {site} | {count} | {pct}% |")
            
            lines.append("")
        
        return lines
    
    @staticmethod
    def _section_plant_sites(plant_sites: Dict[str, Any]) -> List[str]:
        """Generate plant site section."""
        lines = [
            "## Spike Plant Sites",
            ""
        ]
        
        if not plant_sites:
            lines.append("*No spike plant data available*")
            lines.append("")
            return lines
        
        for map_name, data in sorted(plant_sites.items()):
            lines.append(f"### {map_name}")
            lines.append("")
            lines.append("| Site | Plants |")
            lines.append("|------|--------|")
            
            counts = data.get("counts", {})
            for site, count in sorted(counts.items(), key=lambda x: x[1], reverse=True):
                lines.append(f"| {site} | {count} |")
            
            lines.append("")
        
        return lines
    
    @staticmethod
    def _section_opening_duels(opening_duels: Dict[str, Any]) -> List[str]:
        """Generate opening duel leaders section."""
        lines = [
            "## Opening Duel Leaders",
            ""
        ]
        
        if not opening_duels:
            lines.append("*No opening duel data available*")
            lines.append("")
            return lines
        
        lines.append("| Player | Kills | Deaths | Net |")
        lines.append("|--------|-------|--------|-----|")
        
        for player, stats in list(opening_duels.items())[:10]:
            kills = stats.get("first_kills", 0)
            deaths = stats.get("first_deaths", 0)
            net = stats.get("net", 0)
            lines.append(f"| {player} | {kills} | {deaths} | {net:+d} |")
        
        lines.append("")
        return lines
    
    @staticmethod
    def _section_comps(comp_frequency: Dict[str, Any]) -> List[str]:
        """Generate agent composition section."""
        lines = [
            "## Agent Compositions",
            ""
        ]
        
        insufficient = comp_frequency.get("insufficient_data", True)
        if insufficient:
            lines.append("*Insufficient agent composition data in available files*")
            lines.append("")
            return lines
        
        comps_by_map = comp_frequency.get("by_map", {})
        if not comps_by_map:
            lines.append("*No composition data available*")
            lines.append("")
            return lines
        
        for map_name, data in sorted(comps_by_map.items()):
            lines.append(f"### {map_name}")
            lines.append("")
            
            compositions = data.get("compositions", {})
            for comp, count in sorted(compositions.items(), key=lambda x: x[1], reverse=True)[:5]:
                lines.append(f"- **{comp}** ({count}x)")
            
            lines.append("")
        
        return lines
    
    @staticmethod
    def _section_summary(
        maps_played: Dict[str, Any],
        attack_site_preference: Dict[str, Any],
        opening_duels: Dict[str, Any]
    ) -> List[str]:
        """Generate TL;DR summary section."""
        lines = [
            "## TL;DR - Key Takeaways",
            ""
        ]
        
        # Most played map
        maps = maps_played.get("maps", {})
        if maps:
            most_played_map = max(maps.items(), key=lambda x: x[1])
            lines.append(f"- **Most played map:** {most_played_map[0]} ({most_played_map[1]} times)")
        
        # Most common site
        for map_name, data in list(attack_site_preference.items())[:1]:
            counts = data.get("counts", {})
            if counts:
                most_common_site = max(counts.items(), key=lambda x: x[1])
                lines.append(f"- **Primary site ({map_name}):** {most_common_site[0]}")
        
        # Top duel player
        if opening_duels:
            top_player = list(opening_duels.items())[0]
            net = top_player[1].get("net", 0)
            lines.append(f"- **Strongest duel player:** {top_player[0]} (Net: {net:+d})")
        
        lines.append("")
        
        return lines
