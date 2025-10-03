#!/usr/bin/env python3
"""
F1 Race Data Retrieval Script

This script retrieves comprehensive data about a given F1 race using the FastF1 API.
It collects race results, lap times, telemetry, weather data, and more.

Usage:
    python f1_race_data.py --year 2023 --race 5 --session R
    python f1_race_data.py --year 2023 --event "Monaco Grand Prix" --session R
"""

import argparse
import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Union

import fastf1
import pandas as pd


class F1RaceDataCollector:
    """Comprehensive F1 race data collector using FastF1 API."""
    
    def __init__(self, cache_dir: str = "./f1_cache"):
        """Initialize the data collector with caching enabled."""
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
        fastf1.Cache.enable_cache(str(self.cache_dir))
        self.session = None
        self.data = {}
        
    def load_session(self, year: int, race: Union[int, str], session_type: str) -> bool:
        """
        Load a specific F1 session.
        
        Args:
            year: Race year
            race: Race number (1-24) or event name (e.g., "Monaco Grand Prix")
            session_type: Session type ('FP1', 'FP2', 'FP3', 'Q', 'R', 'S')
            
        Returns:
            bool: True if session loaded successfully, False otherwise
        """
        try:
            print(f"Loading {year} {race} {session_type} session...")
            self.session = fastf1.get_session(year, race, session_type)
            self.session.load()
            print("Session loaded successfully!")
            return True
        except Exception as e:
            print(f"Error loading session: {e}")
            return False
    
    def get_event_info(self) -> Dict:
        """Get comprehensive event information."""
        if not self.session:
            return {}
            
        event = self.session.event
        return {
            "event_name": getattr(event, 'EventName', 'Unknown'),
            "location": getattr(event, 'Location', 'Unknown'),
            "country": getattr(event, 'Country', 'Unknown'),
            "circuit_name": getattr(event, 'Location', 'Unknown'),
            "date": event.EventDate.strftime("%Y-%m-%d") if hasattr(event, 'EventDate') and event.EventDate else None,
            "session_name": getattr(event, 'SessionName', 'Unknown'),
            "session_date": event.SessionDate.strftime("%Y-%m-%d %H:%M:%S") if hasattr(event, 'SessionDate') and event.SessionDate else None,
            "session_type": getattr(event, 'SessionType', 'Unknown'),
            "event_format": getattr(event, 'EventFormat', 'Unknown'),
            "f1_api_support": getattr(event, 'F1ApiSupport', False)
        }
    
    def get_session_results(self) -> pd.DataFrame:
        """Get session results (final standings)."""
        if not self.session:
            return pd.DataFrame()
        return self.session.results
    
    def get_lap_data(self) -> pd.DataFrame:
        """Get comprehensive lap-by-lap data."""
        if not self.session:
            return pd.DataFrame()
        return self.session.laps
    
    def get_telemetry_data(self, driver: str = None) -> Dict[str, pd.DataFrame]:
        """
        Get telemetry data for all drivers or a specific driver.
        
        Args:
            driver: Driver abbreviation (e.g., 'VER', 'HAM') or None for all drivers
            
        Returns:
            Dict mapping driver abbreviations to their telemetry DataFrames
        """
        if not self.session:
            return {}
            
        telemetry_data = {}
        laps = self.session.laps
        
        if driver:
            drivers = [driver]
        else:
            drivers = self.session.drivers
            
        for drv in drivers:
            try:
                driver_laps = laps.pick_driver(drv)
                if not driver_laps.empty:
                    telemetry = driver_laps.get_car_data()
                    telemetry_data[drv] = telemetry
            except Exception as e:
                print(f"Error getting telemetry for {drv}: {e}")
                
        return telemetry_data
    
    def get_weather_data(self) -> pd.DataFrame:
        """Get weather data for the session."""
        if not self.session:
            return pd.DataFrame()
        return self.session.weather_data
    
    def get_track_status(self) -> pd.DataFrame:
        """Get track status data (safety car, red flags, etc.)."""
        if not self.session:
            return pd.DataFrame()
        return self.session.track_status
    
    def get_session_status(self) -> pd.DataFrame:
        """Get session status data."""
        if not self.session:
            return pd.DataFrame()
        return self.session.session_status
    
    def get_race_control_messages(self) -> pd.DataFrame:
        """Get race control messages."""
        if not self.session:
            return pd.DataFrame()
        return self.session.race_control_messages
    
    def get_driver_info(self) -> Dict[str, Dict]:
        """Get comprehensive driver information."""
        if not self.session:
            return {}
            
        driver_info = {}
        for driver in self.session.drivers:
            try:
                driver_data = self.session.get_driver(driver)
                driver_info[driver] = {
                    "abbreviation": driver,
                    "full_name": driver_data.FullName,
                    "first_name": driver_data.FirstName,
                    "last_name": driver_data.LastName,
                    "country": driver_data.CountryCode,
                    "team": driver_data.TeamName,
                    "team_color": driver_data.TeamColor,
                    "driver_number": driver_data.DriverNumber
                }
            except Exception as e:
                print(f"Error getting driver info for {driver}: {e}")
                
        return driver_info
    
    def get_team_info(self) -> Dict[str, Dict]:
        """Get comprehensive team information."""
        if not self.session:
            return {}
            
        team_info = {}
        # Get teams from results data instead of session.constructors
        try:
            results = self.session.results
            if not results.empty:
                for _, row in results.iterrows():
                    team_name = row.get('TeamName', 'Unknown')
                    if team_name not in team_info:
                        team_info[team_name] = {
                            "name": team_name,
                            "full_name": team_name,
                            "country": "Unknown"
                        }
        except Exception as e:
            print(f"Error getting team info: {e}")
                
        return team_info
    
    def get_comprehensive_data(self) -> Dict:
        """Collect all available data for the session."""
        print("Collecting comprehensive race data...")
        
        data = {
            "event_info": self.get_event_info(),
            "session_results": self.get_session_results(),
            "lap_data": self.get_lap_data(),
            "weather_data": self.get_weather_data(),
            "track_status": self.get_track_status(),
            "session_status": self.get_session_status(),
            "race_control_messages": self.get_race_control_messages(),
            "driver_info": self.get_driver_info(),
            "team_info": self.get_team_info(),
            "telemetry_data": self.get_telemetry_data()
        }
        
        self.data = data
        return data
    
    def save_data(self, output_dir: str = "./f1_data_output", format: str = "json") -> None:
        """
        Save collected data to files.
        
        Args:
            output_dir: Directory to save data files
            format: Output format ('json', 'csv', 'excel', 'all')
        """
        if not self.data:
            print("No data to save. Run get_comprehensive_data() first.")
            return
            
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        
        # Create timestamp for unique filenames
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        event_name = self.data.get("event_info", {}).get("event_name", "unknown")
        safe_event_name = "".join(c for c in event_name if c.isalnum() or c in (' ', '-', '_')).rstrip()
        
        if format in ["json", "all"]:
            # Save as JSON
            json_data = {}
            for key, value in self.data.items():
                if isinstance(value, pd.DataFrame):
                    json_data[key] = value.to_dict('records')
                else:
                    json_data[key] = value
            
            json_file = output_path / f"{safe_event_name}_{timestamp}.json"
            with open(json_file, 'w') as f:
                json.dump(json_data, f, indent=2, default=str)
            print(f"Data saved to {json_file}")
        
        if format in ["csv", "all"]:
            # Save DataFrames as CSV
            csv_dir = output_path / f"{safe_event_name}_{timestamp}_csv"
            csv_dir.mkdir(exist_ok=True)
            
            for key, value in self.data.items():
                if isinstance(value, pd.DataFrame) and not value.empty:
                    csv_file = csv_dir / f"{key}.csv"
                    value.to_csv(csv_file, index=False)
                    print(f"{key} saved to {csv_file}")
        
        if format in ["excel", "all"]:
            # Save as Excel with multiple sheets
            excel_file = output_path / f"{safe_event_name}_{timestamp}.xlsx"
            with pd.ExcelWriter(excel_file, engine='openpyxl') as writer:
                for key, value in self.data.items():
                    if isinstance(value, pd.DataFrame) and not value.empty:
                        value.to_excel(writer, sheet_name=key, index=False)
                print(f"Data saved to {excel_file}")
    
    def print_summary(self) -> None:
        """Print a summary of the collected data."""
        if not self.data:
            print("No data available. Load a session first.")
            return
            
        event_info = self.data.get("event_info", {})
        print("\n" + "="*60)
        print("F1 RACE DATA SUMMARY")
        print("="*60)
        print(f"Event: {event_info.get('event_name', 'Unknown')}")
        print(f"Location: {event_info.get('location', 'Unknown')}")
        print(f"Date: {event_info.get('date', 'Unknown')}")
        print(f"Session: {event_info.get('session_name', 'Unknown')}")
        
        # Results summary
        results = self.data.get("session_results")
        if results is not None and not results.empty:
            print(f"\nResults: {len(results)} drivers")
            print("Top 3:")
            for i, (_, row) in enumerate(results.head(3).iterrows()):
                print(f"  {i+1}. {row['Abbreviation']} - {row['FullName']} ({row['TeamName']})")
        
        # Data availability summary
        print(f"\nData Available:")
        for key, value in self.data.items():
            if isinstance(value, pd.DataFrame):
                print(f"  {key}: {len(value)} records")
            elif isinstance(value, dict):
                print(f"  {key}: {len(value)} items")
            else:
                print(f"  {key}: Available")


def main():
    """Main function to run the F1 data collector."""
    parser = argparse.ArgumentParser(description="Retrieve comprehensive F1 race data")
    parser.add_argument("--year", type=int, required=True, help="Race year (e.g., 2023)")
    parser.add_argument("--race", help="Race number (1-24) or event name (e.g., 'Monaco Grand Prix')")
    parser.add_argument("--event", help="Event name (alternative to --race)")
    parser.add_argument("--session", default="R", help="Session type (FP1, FP2, FP3, Q, R, S)")
    parser.add_argument("--output", default="./f1_data_output", help="Output directory")
    parser.add_argument("--format", default="all", choices=["json", "csv", "excel", "all"], 
                       help="Output format")
    parser.add_argument("--cache", default="./f1_cache", help="Cache directory")
    parser.add_argument("--driver", help="Specific driver for telemetry (e.g., 'VER')")
    parser.add_argument("--summary", action="store_true", help="Print data summary")
    
    args = parser.parse_args()
    
    # Determine race identifier
    race_identifier = args.race or args.event
    if not race_identifier:
        print("Error: Must specify either --race or --event")
        sys.exit(1)
    
    # Initialize collector
    collector = F1RaceDataCollector(cache_dir=args.cache)
    
    # Load session
    if not collector.load_session(args.year, race_identifier, args.session):
        print("Failed to load session. Exiting.")
        sys.exit(1)
    
    # Collect data
    data = collector.get_comprehensive_data()
    
    # Print summary if requested
    if args.summary:
        collector.print_summary()
    
    # Save data
    collector.save_data(output_dir=args.output, format=args.format)
    
    print(f"\nData collection complete! Check {args.output} for output files.")


if __name__ == "__main__":
    main()
