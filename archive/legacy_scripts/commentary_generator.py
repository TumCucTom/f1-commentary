#!/usr/bin/env python3
"""
F1 Commentary Generator using Groq API

This script takes interesting F1 race data and converts it into engaging commentary
sentences using the Groq API. It processes incidents, position changes, and track
limits violations to create compelling F1 commentary.

Usage:
    python commentary_generator.py --data_file detailed_telemetry_analysis.json
    python commentary_generator.py --data_file detailed_telemetry_analysis.json --output commentary_output.json
"""

import argparse
import json
import os
import sys
from typing import Dict, List, Optional
import requests
import time
from dotenv import load_dotenv


class F1CommentaryGenerator:
    """Generate F1 commentary from race data using Groq API."""
    
    def __init__(self, api_key: str, model: str = "llama-3.1-8b-instant"):
        """Initialize the commentary generator."""
        self.api_key = api_key
        self.model = model
        self.base_url = "https://api.groq.com/openai/v1/chat/completions"
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
    def _call_groq_api(self, prompt: str, max_retries: int = 3) -> Optional[str]:
        """Call the Groq API with retry logic."""
        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "system",
                    "content": "You are David Crofty, the legendary F1 commentator for Sky Sports. Write commentary in his distinctive style: dramatic, exciting, in-the-moment, with his characteristic phrases and energy. Use his signature expressions like 'OH MY GOODNESS!', 'INCREDIBLE!', 'WHAT A MOMENT!', 'AND HERE WE GO!', 'DRAMA!', 'CONTROVERSY!'. Make it sound like you're commentating live as it happens, with building excitement and dramatic pauses. Be specific about speeds, times, and technical details but deliver them with Crofty's infectious enthusiasm and dramatic flair."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": 0.7,
            "max_tokens": 200
        }
        
        for attempt in range(max_retries):
            try:
                response = requests.post(self.base_url, headers=self.headers, json=payload)
                response.raise_for_status()
                
                result = response.json()
                return result['choices'][0]['message']['content'].strip()
                
            except requests.exceptions.RequestException as e:
                print(f"API call failed (attempt {attempt + 1}): {e}")
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)  # Exponential backoff
                else:
                    return None
        
        return None
    
    def generate_incident_commentary(self, incident: Dict) -> Dict:
        """Generate commentary for an incident."""
        prompt = f"""
        F1 Incident Analysis:
        
        Lap: {incident.get('lap', 'Unknown')}
        Message: {incident.get('message', 'Unknown')}
        Steward Action: {incident.get('steward_action', 'Unknown')}
        
        Telemetry Data:
        """
        
        if 'telemetry_analysis' in incident and incident['telemetry_analysis']:
            for driver, telemetry in incident['telemetry_analysis'].items():
                prompt += f"\n{driver}:\n"
                
                if 'lap_data' in telemetry:
                    for lap_key, lap_data in telemetry['lap_data'].items():
                        prompt += f"  {lap_key}: Position {lap_data.get('position', 'N/A')}, Speed {lap_data.get('speed_fl', 'N/A')} km/h, Lap time {lap_data.get('lap_time', 'N/A')}\n"
                
                if 'analysis' in telemetry and 'anomalies' in telemetry['analysis']:
                    prompt += f"  Anomalies: {telemetry['analysis']['anomalies']}\n"
        
        prompt += "\nCommentate on this incident as if it's happening RIGHT NOW! Use David Crofty's dramatic, live commentary style with his signature phrases and excitement. Make it sound like you're watching it unfold in real-time."
        
        commentary = self._call_groq_api(prompt)
        
        return {
            'incident': incident,
            'commentary': commentary,
            'type': 'incident'
        }
    
    def generate_position_change_commentary(self, position_change: Dict) -> Dict:
        """Generate commentary for a major position change."""
        prompt = f"""
        F1 Position Change Analysis:
        
        Driver: {position_change.get('driver', 'Unknown')}
        Lap: {position_change.get('lap', 'Unknown')}
        Position Change: {position_change.get('from_position', 'N/A')} → {position_change.get('to_position', 'N/A')} ({position_change.get('change', 0):+d} positions)
        Lap Time: {position_change.get('lap_time', 'N/A')}
        Previous Lap Time: {position_change.get('prev_lap_time', 'N/A')}
        Compound: {position_change.get('compound', 'Unknown')}
        Tire Life: {position_change.get('tyre_life', 'N/A')} laps
        
        Telemetry Comparison:
        """
        
        if 'telemetry_comparison' in position_change:
            comparison = position_change['telemetry_comparison']
            prompt += f"Lap Time Change: {comparison.get('lap_time_change', 'N/A')}\n"
            
            if 'speed_changes' in comparison:
                prompt += "Speed Changes:\n"
                for field, change in comparison['speed_changes'].items():
                    prompt += f"  {field}: {change}\n"
            
            if 'sector_changes' in comparison:
                prompt += "Sector Changes:\n"
                for field, change in comparison['sector_changes'].items():
                    prompt += f"  {field}: {change}\n"
            
            if 'tire_changes' in comparison:
                prompt += "Tire Changes:\n"
                for field, change in comparison['tire_changes'].items():
                    prompt += f"  {field}: {change}\n"
            
            if 'anomalies' in comparison:
                prompt += f"Anomalies: {comparison['anomalies']}\n"
        
        prompt += "\nCommentate on this dramatic position change as if it's happening LIVE! Use David Crofty's style with dramatic excitement, building tension, and his signature phrases. Make it sound like you're watching the positions change in real-time with mounting drama!"
        
        commentary = self._call_groq_api(prompt)
        
        return {
            'position_change': position_change,
            'commentary': commentary,
            'type': 'position_change'
        }
    
    def generate_track_limits_commentary(self, violation: Dict) -> Dict:
        """Generate commentary for a track limits violation."""
        prompt = f"""
        F1 Track Limits Violation Analysis:
        
        Driver: {violation.get('driver_abbreviation', 'Unknown')}
        Lap: {violation.get('lap', 'Unknown')}
        Turn: {violation.get('turn', 'Unknown')}
        Deleted Time: {violation.get('deleted_time', 'N/A')}
        Message: {violation.get('message', 'Unknown')}
        
        Telemetry Analysis:
        """
        
        if 'telemetry_analysis' in violation and violation['telemetry_analysis']:
            telemetry = violation['telemetry_analysis']
            
            if 'lap_data' in telemetry:
                prompt += "Lap Data Around Violation:\n"
                for lap_key, lap_data in telemetry['lap_data'].items():
                    prompt += f"  {lap_key}: Speed {lap_data.get('speed_fl', 'N/A')} km/h, Lap time {lap_data.get('lap_time', 'N/A')}\n"
            
            if 'analysis' in telemetry:
                analysis = telemetry['analysis']
                if 'speed_analysis' in analysis:
                    speed_analysis = analysis['speed_analysis']
                    prompt += f"Speed Analysis: {speed_analysis}\n"
                
                if 'anomalies' in analysis:
                    prompt += f"Anomalies: {analysis['anomalies']}\n"
        
        prompt += "\nCommentate on this track limits violation as if it's happening RIGHT NOW! Use David Crofty's dramatic style with his signature excitement and phrases. Make it sound like you're watching the violation happen live with building tension!"
        
        commentary = self._call_groq_api(prompt)
        
        return {
            'violation': violation,
            'commentary': commentary,
            'type': 'track_limits'
        }
    
    def generate_collision_commentary(self, collision: Dict) -> Dict:
        """Generate detailed commentary for a collision."""
        prompt = f"""
        F1 Collision Analysis:
        
        Lap: {collision.get('lap', 'Unknown')}
        Message: {collision.get('message', 'Unknown')}
        Steward Action: {collision.get('steward_action', 'Unknown')}
        
        Detailed Telemetry:
        """
        
        if 'telemetry_analysis' in collision and collision['telemetry_analysis']:
            for driver, telemetry in collision['telemetry_analysis'].items():
                prompt += f"\n{driver}:\n"
                
                if 'lap_data' in telemetry:
                    for lap_key, lap_data in telemetry['lap_data'].items():
                        prompt += f"  {lap_key}:\n"
                        prompt += f"    Position: {lap_data.get('position', 'N/A')}\n"
                        prompt += f"    Lap Time: {lap_data.get('lap_time', 'N/A')}\n"
                        prompt += f"    Speed FL: {lap_data.get('speed_fl', 'N/A')} km/h\n"
                        prompt += f"    Sector 1: {lap_data.get('sector1_time', 'N/A')}\n"
                        prompt += f"    Sector 2: {lap_data.get('sector2_time', 'N/A')}\n"
                        prompt += f"    Sector 3: {lap_data.get('sector3_time', 'N/A')}\n"
                        prompt += f"    Compound: {lap_data.get('compound', 'N/A')}\n"
                        prompt += f"    Tire Life: {lap_data.get('tyre_life', 'N/A')} laps\n"
                
                if 'analysis' in telemetry:
                    analysis = telemetry['analysis']
                    if 'speed_analysis' in analysis:
                        prompt += f"  Speed Analysis: {analysis['speed_analysis']}\n"
                    if 'position_analysis' in analysis:
                        prompt += f"  Position Analysis: {analysis['position_analysis']}\n"
                    if 'anomalies' in analysis:
                        prompt += f"  Anomalies: {analysis['anomalies']}\n"
        
        prompt += "\nCommentate on this collision as if it's happening LIVE RIGHT NOW! Use David Crofty's dramatic, breathless commentary style with his signature phrases and building excitement. Make it sound like you're watching the collision unfold in real-time with mounting drama and tension!"
        
        commentary = self._call_groq_api(prompt)
        
        return {
            'collision': collision,
            'commentary': commentary,
            'type': 'collision'
        }
    
    def generate_race_summary_commentary(self, race_data: Dict) -> Dict:
        """Generate overall race summary commentary."""
        prompt = f"""
        F1 Race Summary Analysis:
        
        Race Overview:
        - Total Laps: {race_data.get('race_overview', {}).get('total_laps', 'Unknown')}
        - Winner: {race_data.get('race_overview', {}).get('winner', {}).get('name', 'Unknown')} ({race_data.get('race_overview', {}).get('winner', {}).get('team', 'Unknown')})
        
        Key Statistics:
        - Total Incidents: {race_data.get('statistics', {}).get('total_incidents', 0)}
        - Major Position Changes: {race_data.get('statistics', {}).get('major_changes_5plus', 0)}
        - Track Limits Violations: {race_data.get('statistics', {}).get('track_limits_violations', 0)}
        - Yellow Flag Periods: {race_data.get('statistics', {}).get('yellow_flag_periods', 0)}
        
        Top Commentary Segments: {len(race_data.get('commentary_segments', []))}
        
        Commentate on this race as if you're doing the final summary LIVE! Use David Crofty's dramatic, emotional style with his signature phrases and excitement. Make it sound like you're wrapping up an incredible race with all the drama and tension that unfolded!
        """
        
        commentary = self._call_groq_api(prompt)
        
        return {
            'race_summary': race_data,
            'commentary': commentary,
            'type': 'race_summary'
        }
    
    def process_race_data(self, race_data: Dict) -> List[Dict]:
        """Process all race data and generate commentary."""
        commentaries = []
        
        print("Generating commentary for incidents...")
        incidents = race_data.get('incidents', [])
        for incident in incidents[:5]:  # Top 5 incidents
            commentary = self.generate_incident_commentary(incident)
            if commentary['commentary']:
                commentaries.append(commentary)
                print(f"✓ Generated incident commentary for Lap {incident.get('lap', 'Unknown')}")
            time.sleep(1)  # Rate limiting
        
        print("Generating commentary for major position changes...")
        position_changes = race_data.get('major_position_changes', [])
        for change in position_changes[:5]:  # Top 5 position changes
            commentary = self.generate_position_change_commentary(change)
            if commentary['commentary']:
                commentaries.append(commentary)
                print(f"✓ Generated position change commentary for {change.get('driver', 'Unknown')} Lap {change.get('lap', 'Unknown')}")
            time.sleep(1)  # Rate limiting
        
        print("Generating commentary for track limits violations...")
        violations = race_data.get('track_limits_violations', [])
        for violation in violations[:3]:  # Top 3 violations
            commentary = self.generate_track_limits_commentary(violation)
            if commentary['commentary']:
                commentaries.append(commentary)
                print(f"✓ Generated track limits commentary for {violation.get('driver_abbreviation', 'Unknown')} Lap {violation.get('lap', 'Unknown')}")
            time.sleep(1)  # Rate limiting
        
        print("Generating commentary for collisions...")
        collisions = [inc for inc in incidents if 'COLLISION' in inc.get('message', '')]
        for collision in collisions[:2]:  # Top 2 collisions
            commentary = self.generate_collision_commentary(collision)
            if commentary['commentary']:
                commentaries.append(commentary)
                print(f"✓ Generated collision commentary for Lap {collision.get('lap', 'Unknown')}")
            time.sleep(1)  # Rate limiting
        
        print("Generating race summary commentary...")
        summary_commentary = self.generate_race_summary_commentary(race_data)
        if summary_commentary['commentary']:
            commentaries.append(summary_commentary)
            print("✓ Generated race summary commentary")
        
        return commentaries


def main():
    """Main function to run the commentary generator."""
    # Load environment variables from .env file
    load_dotenv()
    
    parser = argparse.ArgumentParser(description="Generate F1 commentary from race data using Groq API")
    parser.add_argument("--data_file", required=True, help="JSON file containing race analysis data")
    parser.add_argument("--output", default="commentary_output.json", help="Output file for generated commentary")
    parser.add_argument("--api_key", help="Groq API key (or set GROQ_API_KEY environment variable)")
    parser.add_argument("--model", default="llama-3.1-8b-instant", help="Groq model to use")
    
    args = parser.parse_args()
    
    # Get API key
    api_key = args.api_key or os.getenv('GROQ_API_KEY')
    if not api_key:
        print("Error: Groq API key required. Set GROQ_API_KEY environment variable or use --api_key")
        print("Make sure your .env file contains: GROQ_API_KEY=your_api_key_here")
        sys.exit(1)
    
    # Load race data
    try:
        with open(args.data_file, 'r') as f:
            race_data = json.load(f)
        print(f"Loaded race data from {args.data_file}")
    except Exception as e:
        print(f"Error loading race data: {e}")
        sys.exit(1)
    
    # Initialize generator
    generator = F1CommentaryGenerator(api_key, args.model)
    
    # Generate commentary
    print("Starting commentary generation...")
    commentaries = generator.process_race_data(race_data)
    
    # Save results
    output_data = {
        'race_info': {
            'data_file': args.data_file,
            'model_used': args.model,
            'total_commentaries': len(commentaries)
        },
        'commentaries': commentaries
    }
    
    with open(args.output, 'w') as f:
        json.dump(output_data, f, indent=2, default=str)
    
    print(f"\nCommentary generation complete!")
    print(f"Generated {len(commentaries)} commentary pieces")
    print(f"Results saved to {args.output}")
    
    # Print sample commentaries
    print("\n" + "="*60)
    print("SAMPLE COMMENTARIES")
    print("="*60)
    
    for i, commentary in enumerate(commentaries[:3]):
        print(f"\n{i+1}. {commentary['type'].upper()}:")
        print(f"   {commentary['commentary']}")


if __name__ == "__main__":
    main()
