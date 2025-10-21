#!/usr/bin/env python3
"""
Generate Incident Visualizations from Commentary Data

This script automatically extracts incident information from commentary data and generates
animated visualizations showing what happened during specific incidents.

Usage:
    python generate_incident_visualizations.py --commentary crofty_commentary_v3.json --race "Hungary" --year 2024
"""

import argparse
import json
import os
import sys
from datetime import datetime, timedelta
import subprocess


def load_commentary_data(commentary_file: str) -> dict:
    """Load commentary data from JSON file."""
    try:
        with open(commentary_file, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading commentary data: {e}")
        return None


def extract_incident_info(commentary_data: dict) -> list:
    """Extract incident information from commentary data."""
    incidents = []
    
    for commentary in commentary_data.get('commentaries', []):
        if commentary['type'] in ['incident', 'collision']:
            incident_data = commentary.get('incident', commentary.get('collision', {}))
            
            # Extract basic info
            lap = incident_data.get('lap')
            message = incident_data.get('message', '')
            drivers = incident_data.get('drivers', [])
            
            if lap:
                # Try to extract driver codes from the message or drivers list
                driver1 = None
                driver2 = None
                
                # Look for driver codes in the message
                if 'VER' in message:
                    driver1 = 'VER'
                elif 'HAM' in message:
                    if driver1 is None:
                        driver1 = 'HAM'
                    else:
                        driver2 = 'HAM'
                elif 'NOR' in message:
                    if driver1 is None:
                        driver1 = 'NOR'
                    else:
                        driver2 = 'NOR'
                elif 'PIA' in message:
                    if driver1 is None:
                        driver1 = 'PIA'
                    else:
                        driver2 = 'PIA'
                elif 'LEC' in message:
                    if driver1 is None:
                        driver1 = 'LEC'
                    else:
                        driver2 = 'LEC'
                
                # If we couldn't extract from message, try drivers list
                if not driver1 or not driver2:
                    if len(drivers) >= 1:
                        # Convert car numbers to driver codes (this is a simplified mapping)
                        car_to_driver = {
                            '1': 'VER', '44': 'HAM', '4': 'NOR', '81': 'PIA',
                            '16': 'LEC', '55': 'SAI', '11': 'PER', '63': 'RUS',
                            '22': 'TSU', '18': 'STR', '14': 'ALO', '3': 'RIC',
                            '27': 'HUL', '23': 'ALB', '20': 'MAG', '77': 'BOT',
                            '2': 'SAR', '31': 'OCO', '24': 'ZHO', '10': 'GAS'
                        }
                        
                        if not driver1:
                            driver1 = car_to_driver.get(drivers[0], drivers[0])
                        if not driver2 and len(drivers) >= 2:
                            driver2 = car_to_driver.get(drivers[1], drivers[1])
                
                # For single driver incidents, we need to find a second driver to compare with
                # Let's use a common opponent or create a generic comparison
                if driver1 and not driver2:
                    # Try to find a second driver from the telemetry analysis
                    telemetry_analysis = incident_data.get('telemetry_analysis', {})
                    available_drivers = list(telemetry_analysis.keys())
                    
                    if len(available_drivers) >= 2:
                        driver2 = available_drivers[1] if available_drivers[1] != driver1 else available_drivers[0]
                    else:
                        # Use a common opponent based on the first driver
                        common_opponents = {
                            'VER': 'HAM', 'HAM': 'VER', 'NOR': 'PIA', 'PIA': 'NOR',
                            'LEC': 'SAI', 'SAI': 'LEC'
                        }
                        driver2 = common_opponents.get(driver1, 'HAM')  # Default to HAM
                
                if driver1 and driver2:
                    incidents.append({
                        'lap': lap,
                        'driver1': driver1,
                        'driver2': driver2,
                        'message': message,
                        'type': commentary['type'],
                        'commentary': commentary.get('commentary', '')
                    })
    
    return incidents


def estimate_incident_time(lap: int, race_start_time: str = "13:00:00") -> str:
    """
    Estimate the time when an incident occurred based on lap number.
    This is a rough estimation - in reality you'd need more precise timing data.
    """
    try:
        # Parse race start time
        start_hour, start_min, start_sec = map(int, race_start_time.split(':'))
        start_seconds = start_hour * 3600 + start_min * 60 + start_sec
        
        # Estimate: each lap takes about 1 minute 30 seconds on average
        # This is a rough estimate and should be adjusted based on the actual track
        lap_duration = 90  # seconds per lap
        incident_seconds = start_seconds + (lap - 1) * lap_duration
        
        # Convert back to HH:MM:SS
        incident_hour = incident_seconds // 3600
        incident_min = (incident_seconds % 3600) // 60
        incident_sec = incident_seconds % 60
        
        return f"{incident_hour:02d}:{incident_min:02d}:{incident_sec:02d}"
    except:
        return "13:30:00"  # Fallback time


def generate_incident_visualization(incident: dict, year: int, race: str, 
                                  output_dir: str = "incident_visualizations") -> bool:
    """Generate visualization for a specific incident."""
    try:
        # Create output directory if it doesn't exist
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        # Estimate incident time
        incident_time = estimate_incident_time(incident['lap'])
        
        # Duration: 30 seconds should be enough to show most incidents
        duration = 30
        
        print(f"\nGenerating visualization for {incident['type'].upper()} on Lap {incident['lap']}")
        print(f"Drivers: {incident['driver1']} vs {incident['driver2']}")
        print(f"Estimated time: {incident_time}")
        print(f"Message: {incident['message'][:100]}...")
        
        # Get the original directory first
        original_dir = os.getcwd()
        
        # Build command for race_incident_follow.py
        cmd = [
            'python', os.path.join(original_dir, 'race_incident_follow.py'),
            '--year', str(year),
            '--race', race,
            '--driver1', incident['driver1'],
            '--driver2', incident['driver2'],
            '--lap', str(incident['lap']),
            '--start_time', incident_time,
            '--duration', str(duration),
            '--follow',
            '--road',
            '--gif-seconds', '10'  # 10 second GIF
        ]
        
        try:
            # Run the command
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300, cwd=original_dir)
            
            if result.returncode == 0:
                print(f"✅ Successfully generated visualization for Lap {incident['lap']}")
                return True
            else:
                print(f"❌ Failed to generate visualization for Lap {incident['lap']}")
                print(f"Error: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"❌ Error running command: {e}")
            return False
            
    except subprocess.TimeoutExpired:
        print(f"⏰ Timeout generating visualization for Lap {incident['lap']}")
        return False
    except Exception as e:
        print(f"❌ Error generating visualization for Lap {incident['lap']}: {e}")
        return False


def create_incident_summary(incidents: list, output_file: str = "incident_summary.md") -> None:
    """Create a markdown summary of all incidents with their visualizations."""
    with open(output_file, 'w') as f:
        f.write("# F1 Race Incident Visualizations\n\n")
        f.write("This document contains visualizations of key incidents from the race, generated from commentary data.\n\n")
        
        for i, incident in enumerate(incidents, 1):
            f.write(f"## {i}. {incident['type'].upper()} - Lap {incident['lap']}\n\n")
            f.write(f"**Drivers:** {incident['driver1']} vs {incident['driver2']}\n\n")
            f.write(f"**Message:** {incident['message']}\n\n")
            f.write(f"**Commentary:**\n```\n{incident['commentary']}\n```\n\n")
            
            # Add visualization if it exists
            gif_filename = f"commentary_segment_{incident['lap']}_2024_Hungarian_Grand_Prix_{incident['driver1']}_vs_{incident['driver2']}_animated.gif"
            if os.path.exists(f"incident_visualizations/{gif_filename}"):
                f.write(f"**Visualization:**\n")
                f.write(f"![Incident Visualization](incident_visualizations/{gif_filename})\n\n")
            else:
                f.write(f"**Visualization:** *Not generated*\n\n")
            
            f.write("---\n\n")
    
    print(f"Created incident summary: {output_file}")


def main():
    """Main function to handle command line arguments and execute the script."""
    parser = argparse.ArgumentParser(
        description="Generate incident visualizations from commentary data",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python generate_incident_visualizations.py --commentary crofty_commentary_v3.json --race "Hungary" --year 2024
  python generate_incident_visualizations.py --commentary crofty_commentary_v3.json --race "Hungary" --year 2024 --max-incidents 3
        """
    )
    
    parser.add_argument('--commentary', type=str, required=True,
                       help='Path to commentary JSON file')
    parser.add_argument('--race', type=str, required=True,
                       help='Name of the race (e.g., "Hungary", "Monaco")')
    parser.add_argument('--year', type=int, required=True,
                       help='Year of the race (e.g., 2024)')
    parser.add_argument('--max-incidents', type=int, default=5,
                       help='Maximum number of incidents to visualize (default: 5)')
    parser.add_argument('--output-dir', type=str, default='incident_visualizations',
                       help='Output directory for visualizations (default: incident_visualizations)')
    parser.add_argument('--race-start-time', type=str, default='13:00:00',
                       help='Race start time in HH:MM:SS format (default: 13:00:00)')
    
    args = parser.parse_args()
    
    # Load commentary data
    print(f"Loading commentary data from {args.commentary}...")
    commentary_data = load_commentary_data(args.commentary)
    
    if not commentary_data:
        print("❌ Failed to load commentary data")
        sys.exit(1)
    
    # Extract incident information
    print("Extracting incident information...")
    incidents = extract_incident_info(commentary_data)
    
    if not incidents:
        print("❌ No incidents found in commentary data")
        sys.exit(1)
    
    print(f"Found {len(incidents)} incidents")
    
    # Limit number of incidents to process
    incidents_to_process = incidents[:args.max_incidents]
    print(f"Processing {len(incidents_to_process)} incidents...")
    
    # Generate visualizations
    successful_visualizations = 0
    for incident in incidents_to_process:
        if generate_incident_visualization(incident, args.year, args.race, args.output_dir):
            successful_visualizations += 1
    
    print(f"\n✅ Successfully generated {successful_visualizations}/{len(incidents_to_process)} visualizations")
    
    # Create summary document
    create_incident_summary(incidents_to_process)
    
    print(f"\n📁 Visualizations saved to: {args.output_dir}/")
    print(f"📄 Summary document: incident_summary.md")


if __name__ == "__main__":
    main()
