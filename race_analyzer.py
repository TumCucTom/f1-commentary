#!/usr/bin/env python3
"""
F1 Race Analyzer - Automatic Race Analysis Tool

This script automatically analyzes F1 race data to identify:
- Key incidents and collisions
- Major position changes
- Pit stop strategies
- Yellow flag periods
- Track limits violations
- Interesting commentary segments

Usage:
    python race_analyzer.py --data_dir ./f1_data_output --race "Hungarian Grand Prix"
    python race_analyzer.py --data_dir ./f1_data_output --race "Hungarian Grand Prix" --output ./analysis_results
"""

import argparse
import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union

import pandas as pd
import numpy as np


class F1RaceAnalyzer:
    """Comprehensive F1 race analysis tool."""
    
    def __init__(self, data_dir: str):
        """Initialize the analyzer with race data directory."""
        self.data_dir = Path(data_dir)
        self.lap_data = None
        self.race_control = None
        self.track_status = None
        self.session_results = None
        self.weather_data = None
        self.session_status = None
        self.analysis_results = {}
        
    def load_race_data(self, race_name: str) -> bool:
        """
        Load race data from CSV files.
        
        Args:
            race_name: Name of the race (used to find data files)
            
        Returns:
            bool: True if data loaded successfully, False otherwise
        """
        try:
            # Find the most recent data files for this race
            csv_dir = None
            for item in self.data_dir.iterdir():
                if item.is_dir() and race_name.lower().replace(" ", " ") in item.name.lower():
                    csv_dir = item
                    break
            
            if not csv_dir:
                print(f"Error: No data found for race '{race_name}' in {self.data_dir}")
                return False
            
            # Load all CSV files
            self.lap_data = pd.read_csv(csv_dir / 'lap_data.csv')
            self.race_control = pd.read_csv(csv_dir / 'race_control_messages.csv')
            self.track_status = pd.read_csv(csv_dir / 'track_status.csv')
            self.session_results = pd.read_csv(csv_dir / 'session_results.csv')
            self.weather_data = pd.read_csv(csv_dir / 'weather_data.csv')
            self.session_status = pd.read_csv(csv_dir / 'session_status.csv')
            
            print(f"Successfully loaded data for {race_name}")
            print(f"  - {len(self.lap_data)} lap records")
            print(f"  - {len(self.race_control)} race control messages")
            print(f"  - {len(self.weather_data)} weather data points")
            
            return True
            
        except Exception as e:
            print(f"Error loading race data: {e}")
            return False
    
    def analyze_race_overview(self) -> Dict:
        """Analyze basic race information."""
        if self.lap_data is None:
            return {}
        
        # Get race winner from results
        winner = self.session_results.iloc[0] if not self.session_results.empty else None
        
        return {
            'total_laps': int(self.lap_data['LapNumber'].max()),
            'total_drivers': self.lap_data['Driver'].nunique(),
            'total_lap_records': len(self.lap_data),
            'winner': {
                'driver': winner['Abbreviation'] if winner is not None else 'Unknown',
                'name': winner['FullName'] if winner is not None else 'Unknown',
                'team': winner['TeamName'] if winner is not None else 'Unknown',
                'time': str(winner['Time']) if winner is not None else 'Unknown',
                'points': winner['Points'] if winner is not None else 0
            } if winner is not None else None,
            'podium': [
                {
                    'position': i + 1,
                    'driver': row['Abbreviation'],
                    'name': row['FullName'],
                    'team': row['TeamName'],
                    'gap': str(row['Time']) if i == 0 else f"+{row['Time']}"
                }
                for i, (_, row) in enumerate(self.session_results.head(3).iterrows())
            ] if not self.session_results.empty else []
        }
    
    def analyze_incidents(self) -> List[Dict]:
        """Analyze all incidents and collisions with detailed telemetry data."""
        if self.race_control is None or self.lap_data is None:
            return []
        
        incidents = []
        
        # Find incident-related messages
        incident_keywords = ['INCIDENT', 'CRASH', 'COLLISION', 'OFF TRACK', 'SPIN', 'CONTACT']
        incident_messages = self.race_control[
            self.race_control['Message'].str.contains('|'.join(incident_keywords), case=False, na=False)
        ]
        
        for _, incident in incident_messages.iterrows():
            # Extract driver information from message
            drivers = []
            if 'CAR' in incident['Message']:
                # Extract car numbers from message
                import re
                car_numbers = re.findall(r'CAR (\d+)', incident['Message'])
                drivers = car_numbers
            
            incident_lap = int(incident['Lap']) if not pd.isna(incident['Lap']) else None
            
            # Get detailed telemetry analysis for this incident
            telemetry_analysis = self._analyze_incident_telemetry(incident_lap, drivers)
            
            incidents.append({
                'lap': incident_lap,
                'time': str(incident['Time']),
                'message': incident['Message'],
                'category': incident.get('Category', 'Unknown'),
                'drivers': drivers,
                'steward_action': self._get_steward_action(incident['Message']),
                'telemetry_analysis': telemetry_analysis
            })
        
        return incidents
    
    def _get_steward_action(self, message: str) -> str:
        """Extract steward action from message."""
        if 'NO FURTHER ACTION' in message:
            return 'No further action'
        elif 'UNDER INVESTIGATION' in message:
            return 'Under investigation'
        elif 'WILL BE INVESTIGATED' in message:
            return 'Will be investigated after race'
        elif 'DELETED' in message:
            return 'Lap time deleted'
        elif 'NOTED' in message:
            return 'Noted'
        else:
            return 'Unknown'
    
    def _analyze_incident_telemetry(self, incident_lap: int, drivers: List[str]) -> Dict:
        """Analyze detailed telemetry data around incidents."""
        if not incident_lap or not drivers or self.lap_data is None:
            return {}
        
        telemetry_analysis = {}
        
        for driver_num in drivers:
            # Find driver abbreviation from car number
            driver_abbrev = self._get_driver_from_car_number(driver_num)
            if not driver_abbrev:
                continue
            
            # Get laps around the incident (2 laps before, incident lap, 2 laps after)
            analysis_laps = [incident_lap - 2, incident_lap - 1, incident_lap, incident_lap + 1, incident_lap + 2]
            driver_telemetry = {}
            
            for lap_num in analysis_laps:
                if lap_num <= 0:
                    continue
                    
                lap_data = self.lap_data[
                    (self.lap_data['Driver'] == driver_abbrev) & 
                    (self.lap_data['LapNumber'] == lap_num)
                ]
                
                if not lap_data.empty:
                    lap_info = lap_data.iloc[0]
                    
                    # Extract telemetry data
                    telemetry_data = {
                        'lap_number': int(lap_num),
                        'lap_time': str(lap_info.get('LapTime', 'N/A')),
                        'position': int(lap_info.get('Position', 0)) if not pd.isna(lap_info.get('Position')) else None,
                        'sector1_time': str(lap_info.get('Sector1Time', 'N/A')),
                        'sector2_time': str(lap_info.get('Sector2Time', 'N/A')),
                        'sector3_time': str(lap_info.get('Sector3Time', 'N/A')),
                        'speed_i1': float(lap_info.get('SpeedI1', 0)) if not pd.isna(lap_info.get('SpeedI1')) else None,
                        'speed_i2': float(lap_info.get('SpeedI2', 0)) if not pd.isna(lap_info.get('SpeedI2')) else None,
                        'speed_fl': float(lap_info.get('SpeedFL', 0)) if not pd.isna(lap_info.get('SpeedFL')) else None,
                        'speed_st': float(lap_info.get('SpeedST', 0)) if not pd.isna(lap_info.get('SpeedST')) else None,
                        'compound': lap_info.get('Compound', 'Unknown'),
                        'tyre_life': int(lap_info.get('TyreLife', 0)) if not pd.isna(lap_info.get('TyreLife')) else None,
                        'is_personal_best': bool(lap_info.get('IsPersonalBest', False)),
                        'track_status': int(lap_info.get('TrackStatus', 1)) if not pd.isna(lap_info.get('TrackStatus')) else 1
                    }
                    
                    # Add detailed car telemetry data if available
                    car_telemetry = self._get_car_telemetry_data(driver_abbrev, lap_num)
                    if car_telemetry:
                        telemetry_data.update(car_telemetry)
                    
                    driver_telemetry[f'lap_{lap_num}'] = telemetry_data
            
            # Analyze patterns and changes
            if driver_telemetry:
                analysis = self._analyze_telemetry_patterns(driver_telemetry, incident_lap)
                telemetry_analysis[driver_abbrev] = {
                    'driver_number': driver_num,
                    'lap_data': driver_telemetry,
                    'analysis': analysis
                }
        
        return telemetry_analysis
    
    def _get_driver_from_car_number(self, car_number: str) -> Optional[str]:
        """Get driver abbreviation from car number."""
        if self.session_results is None:
            return None
        
        driver_row = self.session_results[self.session_results['DriverNumber'] == int(car_number)]
        if not driver_row.empty:
            return driver_row.iloc[0]['Abbreviation']
        return None
    
    def _get_car_telemetry_data(self, driver_abbrev: str, lap_num: int) -> Optional[Dict]:
        """Get detailed car telemetry data for a specific driver and lap."""
        try:
            import fastf1
            fastf1.Cache.enable_cache('./f1_cache')
            
            # Load session data
            session = fastf1.get_session(2024, 'Hungarian Grand Prix', 'R')
            session.load()
            
            # Get driver laps
            laps = session.laps
            driver_laps = laps.pick_driver(driver_abbrev)
            
            if driver_laps.empty:
                return None
            
            # Get the specific lap
            lap_data = driver_laps[driver_laps['LapNumber'] == lap_num]
            if lap_data.empty:
                return None
            
            # Get car telemetry for this lap
            telemetry = lap_data.get_car_data()
            
            if telemetry.empty:
                return None
            
            # Calculate statistics for the lap
            telemetry_stats = {
                'avg_rpm': float(telemetry['RPM'].mean()) if not telemetry['RPM'].isna().all() else None,
                'max_rpm': float(telemetry['RPM'].max()) if not telemetry['RPM'].isna().all() else None,
                'avg_throttle': float(telemetry['Throttle'].mean()) if not telemetry['Throttle'].isna().all() else None,
                'max_throttle': float(telemetry['Throttle'].max()) if not telemetry['Throttle'].isna().all() else None,
                'avg_brake': float(telemetry['Brake'].mean()) if not telemetry['Brake'].isna().all() else None,
                'max_brake': float(telemetry['Brake'].max()) if not telemetry['Brake'].isna().all() else None,
                'avg_speed': float(telemetry['Speed'].mean()) if not telemetry['Speed'].isna().all() else None,
                'max_speed': float(telemetry['Speed'].max()) if not telemetry['Speed'].isna().all() else None,
                'gear_changes': int((telemetry['nGear'].diff() != 0).sum()) if not telemetry['nGear'].isna().all() else None,
                'drs_usage': float(telemetry['DRS'].mean()) if not telemetry['DRS'].isna().all() else None,
                'brake_lock_events': int((telemetry['Brake'] > 0.8).sum()) if not telemetry['Brake'].isna().all() else None,
                'throttle_application': float((telemetry['Throttle'] > 0.5).mean()) if not telemetry['Throttle'].isna().all() else None
            }
            
            return telemetry_stats
            
        except Exception as e:
            print(f"Error getting car telemetry for {driver_abbrev} lap {lap_num}: {e}")
            return None
    
    def _analyze_telemetry_patterns(self, telemetry_data: Dict, incident_lap: int) -> Dict:
        """Analyze telemetry patterns around incidents."""
        analysis = {
            'speed_analysis': {},
            'sector_analysis': {},
            'tire_analysis': {},
            'position_analysis': {},
            'anomalies': []
        }
        
        # Speed analysis
        speeds = {}
        for lap_key, data in telemetry_data.items():
            if data['speed_fl'] is not None:
                speeds[lap_key] = data['speed_fl']
        
        if len(speeds) >= 2:
            speed_values = list(speeds.values())
            analysis['speed_analysis'] = {
                'max_speed': max(speed_values),
                'min_speed': min(speed_values),
                'speed_variance': max(speed_values) - min(speed_values),
                'incident_lap_speed': speeds.get(f'lap_{incident_lap}', None)
            }
            
            # Check for significant speed drops
            if f'lap_{incident_lap}' in speeds and f'lap_{incident_lap-1}' in speeds:
                speed_drop = speeds[f'lap_{incident_lap-1}'] - speeds[f'lap_{incident_lap}']
                if speed_drop > 20:  # Significant speed drop
                    analysis['anomalies'].append(f"Significant speed drop: {speed_drop:.1f} km/h")
        
        # Sector time analysis
        sector_times = {}
        for lap_key, data in telemetry_data.items():
            if data['sector1_time'] != 'N/A':
                sector_times[lap_key] = {
                    'sector1': data['sector1_time'],
                    'sector2': data['sector2_time'],
                    'sector3': data['sector3_time']
                }
        
        if len(sector_times) >= 2:
            # Find slowest sectors
            slowest_sectors = {}
            for sector in ['sector1', 'sector2', 'sector3']:
                sector_values = [data[sector] for data in sector_times.values() if data[sector] != 'N/A']
                if sector_values:
                    slowest_sectors[sector] = max(sector_values)
            
            analysis['sector_analysis'] = {
                'slowest_sectors': slowest_sectors,
                'incident_lap_sectors': sector_times.get(f'lap_{incident_lap}', {})
            }
        
        # Position analysis
        positions = {}
        for lap_key, data in telemetry_data.items():
            if data['position'] is not None:
                positions[lap_key] = data['position']
        
        if len(positions) >= 2:
            position_values = list(positions.values())
            analysis['position_analysis'] = {
                'position_range': f"{min(position_values)} - {max(position_values)}",
                'position_change': max(position_values) - min(position_values),
                'incident_lap_position': positions.get(f'lap_{incident_lap}', None)
            }
            
            # Check for position drops
            if f'lap_{incident_lap}' in positions and f'lap_{incident_lap-1}' in positions:
                position_drop = positions[f'lap_{incident_lap}'] - positions[f'lap_{incident_lap-1}']
                if position_drop > 0:  # Position got worse
                    analysis['anomalies'].append(f"Position drop: {position_drop} positions")
        
        # Tire analysis
        tire_data = {}
        for lap_key, data in telemetry_data.items():
            if data['compound'] != 'Unknown':
                tire_data[lap_key] = {
                    'compound': data['compound'],
                    'tyre_life': data['tyre_life']
                }
        
        if tire_data:
            analysis['tire_analysis'] = {
                'compounds_used': list(set([data['compound'] for data in tire_data.values()])),
                'incident_lap_tire': tire_data.get(f'lap_{incident_lap}', {}),
                'tire_age_at_incident': tire_data.get(f'lap_{incident_lap}', {}).get('tyre_life', None)
            }
        
        return analysis
    
    def analyze_position_changes(self, min_change: int = 3) -> List[Dict]:
        """Analyze significant position changes with telemetry data."""
        if self.lap_data is None:
            return []
        
        position_changes = []
        
        for driver in self.lap_data['Driver'].unique():
            driver_laps = self.lap_data[self.lap_data['Driver'] == driver].sort_values('LapNumber')
            
            if len(driver_laps) > 1:
                for i in range(1, len(driver_laps)):
                    prev_lap = driver_laps.iloc[i-1]
                    curr_lap = driver_laps.iloc[i]
                    
                    prev_pos = prev_lap['Position']
                    curr_pos = curr_lap['Position']
                    
                    if not pd.isna(prev_pos) and not pd.isna(curr_pos) and prev_pos != curr_pos:
                        change = prev_pos - curr_pos
                        
                        if abs(change) >= min_change:
                            # Get telemetry comparison
                            telemetry_comparison = self._compare_lap_telemetry(prev_lap, curr_lap)
                            
                            position_changes.append({
                                'driver': driver,
                                'lap': int(curr_lap['LapNumber']),
                                'from_position': int(prev_pos),
                                'to_position': int(curr_pos),
                                'change': int(change),
                                'lap_time': str(curr_lap['LapTime']),
                                'prev_lap_time': str(prev_lap['LapTime']),
                                'compound': curr_lap.get('Compound', 'Unknown'),
                                'tyre_life': int(curr_lap.get('TyreLife', 0)) if not pd.isna(curr_lap.get('TyreLife')) else None,
                                'telemetry_comparison': telemetry_comparison
                            })
        
        # Sort by absolute change (biggest changes first)
        position_changes.sort(key=lambda x: abs(x['change']), reverse=True)
        return position_changes
    
    def _compare_lap_telemetry(self, prev_lap: pd.Series, curr_lap: pd.Series) -> Dict:
        """Compare telemetry data between two laps."""
        comparison = {
            'lap_time_change': 'N/A',
            'speed_changes': {},
            'sector_changes': {},
            'tire_changes': {},
            'anomalies': []
        }
        
        # Lap time comparison
        try:
            prev_time = pd.to_timedelta(prev_lap['LapTime']).total_seconds()
            curr_time = pd.to_timedelta(curr_lap['LapTime']).total_seconds()
            time_diff = curr_time - prev_time
            comparison['lap_time_change'] = f"{time_diff:+.3f}s"
            
            if abs(time_diff) > 2.0:  # Significant lap time change
                comparison['anomalies'].append(f"Significant lap time change: {time_diff:+.3f}s")
        except:
            pass
        
        # Speed comparison
        speed_fields = ['SpeedI1', 'SpeedI2', 'SpeedFL', 'SpeedST']
        for field in speed_fields:
            if not pd.isna(prev_lap.get(field)) and not pd.isna(curr_lap.get(field)):
                speed_diff = curr_lap[field] - prev_lap[field]
                comparison['speed_changes'][field] = f"{speed_diff:+.1f} km/h"
                
                if abs(speed_diff) > 15:  # Significant speed change
                    comparison['anomalies'].append(f"Significant {field} change: {speed_diff:+.1f} km/h")
        
        # Sector time comparison
        sector_fields = ['Sector1Time', 'Sector2Time', 'Sector3Time']
        for field in sector_fields:
            if not pd.isna(prev_lap.get(field)) and not pd.isna(curr_lap.get(field)):
                try:
                    prev_sector = pd.to_timedelta(prev_lap[field]).total_seconds()
                    curr_sector = pd.to_timedelta(curr_lap[field]).total_seconds()
                    sector_diff = curr_sector - prev_sector
                    comparison['sector_changes'][field] = f"{sector_diff:+.3f}s"
                    
                    if abs(sector_diff) > 0.5:  # Significant sector change
                        comparison['anomalies'].append(f"Significant {field} change: {sector_diff:+.3f}s")
                except:
                    pass
        
        # Tire comparison
        if prev_lap.get('Compound') != curr_lap.get('Compound'):
            comparison['tire_changes']['compound_change'] = f"{prev_lap.get('Compound', 'Unknown')} → {curr_lap.get('Compound', 'Unknown')}"
        
        prev_tyre_life = prev_lap.get('TyreLife')
        curr_tyre_life = curr_lap.get('TyreLife')
        if not pd.isna(prev_tyre_life) and not pd.isna(curr_tyre_life):
            tyre_life_diff = curr_tyre_life - prev_tyre_life
            comparison['tire_changes']['tyre_life_change'] = f"{tyre_life_diff:+.0f} laps"
        
        return comparison
    
    def analyze_pit_stop_strategies(self) -> Dict:
        """Analyze pit stop strategies for all drivers."""
        if self.lap_data is None:
            return {}
        
        strategies = {}
        
        for driver in self.lap_data['Driver'].unique():
            driver_laps = self.lap_data[self.lap_data['Driver'] == driver].sort_values('LapNumber')
            pit_stops = driver_laps[driver_laps['PitInTime'].notna()]
            
            if not pit_stops.empty:
                driver_strategy = []
                for _, pit in pit_stops.iterrows():
                    lap_num = pit['LapNumber']
                    
                    # Get position before and after pit stop
                    pos_before = None
                    pos_after = None
                    
                    if lap_num > 1:
                        pos_before = driver_laps[driver_laps['LapNumber'] == lap_num - 1]['Position'].iloc[0]
                    if lap_num < driver_laps['LapNumber'].max():
                        pos_after = driver_laps[driver_laps['LapNumber'] == lap_num + 1]['Position'].iloc[0]
                    
                    driver_strategy.append({
                        'lap': int(lap_num),
                        'compound': pit.get('Compound', 'Unknown'),
                        'tyre_life': pit.get('TyreLife', 'Unknown'),
                        'position_before': int(pos_before) if pos_before else None,
                        'position_after': int(pos_after) if pos_after else None,
                        'position_change': int(pos_after - pos_before) if pos_before and pos_after else None
                    })
                
                strategies[driver] = driver_strategy
        
        return strategies
    
    def analyze_track_limits_violations(self) -> List[Dict]:
        """Analyze track limits violations with telemetry data."""
        if self.race_control is None:
            return []
        
        violations = []
        
        # Find track limits messages
        track_limits_messages = self.race_control[
            self.race_control['Message'].str.contains('TRACK LIMITS|DELETED', case=False, na=False)
        ]
        
        for _, violation in track_limits_messages.iterrows():
            # Extract driver and details from message
            import re
            driver_match = re.search(r'CAR (\d+)', violation['Message'])
            time_match = re.search(r'TIME ([0-9:\.]+)', violation['Message'])
            turn_match = re.search(r'TURN (\d+)', violation['Message'])
            
            violation_lap = int(violation['Lap']) if not pd.isna(violation['Lap']) else None
            driver_number = driver_match.group(1) if driver_match else None
            
            # Get telemetry analysis for this violation
            telemetry_analysis = {}
            if violation_lap and driver_number:
                driver_abbrev = self._get_driver_from_car_number(driver_number)
                if driver_abbrev:
                    telemetry_analysis = self._analyze_violation_telemetry(driver_abbrev, violation_lap)
            
            violations.append({
                'lap': violation_lap,
                'time': str(violation['Time']),
                'driver_number': driver_number,
                'driver_abbreviation': self._get_driver_from_car_number(driver_number) if driver_number else None,
                'deleted_time': time_match.group(1) if time_match else None,
                'turn': turn_match.group(1) if turn_match else None,
                'message': violation['Message'],
                'telemetry_analysis': telemetry_analysis
            })
        
        return violations
    
    def _analyze_violation_telemetry(self, driver_abbrev: str, violation_lap: int) -> Dict:
        """Analyze telemetry data around track limits violations."""
        if self.lap_data is None:
            return {}
        
        # Get laps around the violation (1 lap before, violation lap, 1 lap after)
        analysis_laps = [violation_lap - 1, violation_lap, violation_lap + 1]
        telemetry_data = {}
        
        for lap_num in analysis_laps:
            if lap_num <= 0:
                continue
                
            lap_data = self.lap_data[
                (self.lap_data['Driver'] == driver_abbrev) & 
                (self.lap_data['LapNumber'] == lap_num)
            ]
            
            if not lap_data.empty:
                lap_info = lap_data.iloc[0]
                
                telemetry_data[f'lap_{lap_num}'] = {
                    'lap_number': int(lap_num),
                    'lap_time': str(lap_info.get('LapTime', 'N/A')),
                    'position': int(lap_info.get('Position', 0)) if not pd.isna(lap_info.get('Position')) else None,
                    'sector1_time': str(lap_info.get('Sector1Time', 'N/A')),
                    'sector2_time': str(lap_info.get('Sector2Time', 'N/A')),
                    'sector3_time': str(lap_info.get('Sector3Time', 'N/A')),
                    'speed_i1': float(lap_info.get('SpeedI1', 0)) if not pd.isna(lap_info.get('SpeedI1')) else None,
                    'speed_i2': float(lap_info.get('SpeedI2', 0)) if not pd.isna(lap_info.get('SpeedI2')) else None,
                    'speed_fl': float(lap_info.get('SpeedFL', 0)) if not pd.isna(lap_info.get('SpeedFL')) else None,
                    'speed_st': float(lap_info.get('SpeedST', 0)) if not pd.isna(lap_info.get('SpeedST')) else None,
                    'compound': lap_info.get('Compound', 'Unknown'),
                    'tyre_life': int(lap_info.get('TyreLife', 0)) if not pd.isna(lap_info.get('TyreLife')) else None,
                    'is_personal_best': bool(lap_info.get('IsPersonalBest', False))
                }
        
        # Analyze patterns
        analysis = {
            'speed_analysis': {},
            'sector_analysis': {},
            'anomalies': []
        }
        
        # Speed analysis
        speeds = {}
        for lap_key, data in telemetry_data.items():
            if data['speed_fl'] is not None:
                speeds[lap_key] = data['speed_fl']
        
        if len(speeds) >= 2:
            speed_values = list(speeds.values())
            analysis['speed_analysis'] = {
                'max_speed': max(speed_values),
                'min_speed': min(speed_values),
                'violation_lap_speed': speeds.get(f'lap_{violation_lap}', None)
            }
            
            # Check for speed anomalies
            if f'lap_{violation_lap}' in speeds and f'lap_{violation_lap-1}' in speeds:
                speed_diff = speeds[f'lap_{violation_lap}'] - speeds[f'lap_{violation_lap-1}']
                if abs(speed_diff) > 10:
                    analysis['anomalies'].append(f"Speed change: {speed_diff:+.1f} km/h")
        
        # Sector analysis
        if f'lap_{violation_lap}' in telemetry_data:
            violation_lap_data = telemetry_data[f'lap_{violation_lap}']
            analysis['sector_analysis'] = {
                'sector1_time': violation_lap_data['sector1_time'],
                'sector2_time': violation_lap_data['sector2_time'],
                'sector3_time': violation_lap_data['sector3_time']
            }
        
        return {
            'lap_data': telemetry_data,
            'analysis': analysis
        }
    
    def analyze_yellow_flags(self) -> List[Dict]:
        """Analyze yellow flag periods."""
        if self.race_control is None:
            return []
        
        yellow_flags = []
        
        # Find yellow flag messages
        yellow_messages = self.race_control[
            self.race_control['Message'].str.contains('YELLOW', case=False, na=False)
        ]
        
        for _, flag in yellow_messages.iterrows():
            yellow_flags.append({
                'lap': int(flag['Lap']) if not pd.isna(flag['Lap']) else None,
                'time': str(flag['Time']),
                'message': flag['Message'],
                'sector': flag.get('Sector', None)
            })
        
        return yellow_flags
    
    def analyze_weather_impact(self) -> Dict:
        """Analyze weather conditions and their impact."""
        if self.weather_data is None:
            return {}
        
        if self.weather_data.empty:
            return {}
        
        return {
            'air_temperature': {
                'min': float(self.weather_data['AirTemp'].min()),
                'max': float(self.weather_data['AirTemp'].max()),
                'avg': float(self.weather_data['AirTemp'].mean()),
                'unit': 'Celsius'
            },
            'track_temperature': {
                'min': float(self.weather_data['TrackTemp'].min()),
                'max': float(self.weather_data['TrackTemp'].max()),
                'avg': float(self.weather_data['TrackTemp'].mean()),
                'unit': 'Celsius'
            },
            'humidity': {
                'min': float(self.weather_data['Humidity'].min()),
                'max': float(self.weather_data['Humidity'].max()),
                'avg': float(self.weather_data['Humidity'].mean()),
                'unit': 'percent'
            },
            'pressure': {
                'min': float(self.weather_data['Pressure'].min()),
                'max': float(self.weather_data['Pressure'].max()),
                'avg': float(self.weather_data['Pressure'].mean()),
                'unit': 'hPa'
            },
            'wind_speed': {
                'min': float(self.weather_data['WindSpeed'].min()),
                'max': float(self.weather_data['WindSpeed'].max()),
                'avg': float(self.weather_data['WindSpeed'].mean()),
                'unit': 'm/s'
            },
            'rainfall': 'Rain detected' if self.weather_data['Rainfall'].any() else 'No rain detected'
        }
    
    def identify_commentary_segments(self) -> List[Dict]:
        """Identify the most interesting segments for commentary."""
        segments = []
        
        # Get all analysis data
        incidents = self.analyze_incidents()
        position_changes = self.analyze_position_changes(min_change=5)  # Only major changes
        track_limits = self.analyze_track_limits_violations()
        yellow_flags = self.analyze_yellow_flags()
        
        # Priority 1: Major collisions
        collisions = [inc for inc in incidents if 'COLLISION' in inc['message']]
        for collision in collisions:
            segments.append({
                'priority': 1,
                'type': 'collision',
                'lap': collision['lap'],
                'title': f"Collision - Lap {collision['lap']}",
                'description': collision['message'],
                'drivers': collision['drivers'],
                'steward_action': collision['steward_action'],
                'data_points': ['positions', 'lap_times', 'steward_investigation', 'yellow_flag']
            })
        
        # Priority 2: Major position changes
        for change in position_changes[:5]:  # Top 5 biggest changes
            segments.append({
                'priority': 2,
                'type': 'position_change',
                'lap': change['lap'],
                'title': f"{change['driver']} - {change['change']:+d} positions (Lap {change['lap']})",
                'description': f"{change['driver']} drops from {change['from_position']} to {change['to_position']}",
                'driver': change['driver'],
                'change': change['change'],
                'data_points': ['position_change', 'lap_times', 'tire_compound']
            })
        
        # Priority 3: Track limits controversies
        for violation in track_limits:
            segments.append({
                'priority': 3,
                'type': 'track_limits',
                'lap': violation['lap'],
                'title': f"Track Limits - Lap {violation['lap']}",
                'description': violation['message'],
                'driver_number': violation['driver_number'],
                'turn': violation['turn'],
                'data_points': ['steward_decision', 'track_limits', 'racing_standards']
            })
        
        # Priority 4: Yellow flag periods
        for flag in yellow_flags:
            segments.append({
                'priority': 4,
                'type': 'yellow_flag',
                'lap': flag['lap'],
                'title': f"Yellow Flag - Lap {flag['lap']}",
                'description': flag['message'],
                'sector': flag['sector'],
                'data_points': ['track_status', 'safety_periods', 'race_impact']
            })
        
        # Sort by priority
        segments.sort(key=lambda x: x['priority'])
        return segments
    
    def generate_comprehensive_analysis(self) -> Dict:
        """Generate complete race analysis."""
        print("Generating comprehensive race analysis...")
        
        self.analysis_results = {
            'race_overview': self.analyze_race_overview(),
            'incidents': self.analyze_incidents(),
            'major_position_changes': self.analyze_position_changes(min_change=3),
            'pit_stop_strategies': self.analyze_pit_stop_strategies(),
            'track_limits_violations': self.analyze_track_limits_violations(),
            'yellow_flags': self.analyze_yellow_flags(),
            'weather_conditions': self.analyze_weather_impact(),
            'commentary_segments': self.identify_commentary_segments(),
            'statistics': self._generate_statistics()
        }
        
        return self.analysis_results
    
    def _generate_statistics(self) -> Dict:
        """Generate race statistics."""
        if self.lap_data is None:
            return {}
        
        # Count position changes
        position_changes = self.analyze_position_changes(min_change=1)
        
        return {
            'total_position_changes': len(position_changes),
            'significant_changes_3plus': len([c for c in position_changes if abs(c['change']) >= 3]),
            'major_changes_5plus': len([c for c in position_changes if abs(c['change']) >= 5]),
            'total_incidents': len(self.analyze_incidents()),
            'track_limits_violations': len(self.analyze_track_limits_violations()),
            'yellow_flag_periods': len(self.analyze_yellow_flags()),
            'total_pit_stops': len([pit for strategy in self.analyze_pit_stop_strategies().values() for pit in strategy])
        }
    
    def save_analysis(self, output_dir: str = "./analysis_results", format: str = "all") -> None:
        """Save analysis results to files."""
        if not self.analysis_results:
            print("No analysis results to save. Run generate_comprehensive_analysis() first.")
            return
        
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        if format in ["json", "all"]:
            json_file = output_path / f"race_analysis_{timestamp}.json"
            with open(json_file, 'w') as f:
                json.dump(self.analysis_results, f, indent=2, default=str)
            print(f"Analysis saved to {json_file}")
        
        if format in ["txt", "all"]:
            txt_file = output_path / f"race_analysis_{timestamp}.txt"
            with open(txt_file, 'w') as f:
                f.write(self._format_analysis_text())
            print(f"Analysis saved to {txt_file}")
    
    def _format_analysis_text(self) -> str:
        """Format analysis results as readable text."""
        if not self.analysis_results:
            return "No analysis results available."
        
        text = []
        text.append("# F1 Race Analysis Report")
        text.append("=" * 50)
        
        # Race overview
        overview = self.analysis_results.get('race_overview', {})
        text.append(f"\n## Race Overview")
        text.append(f"Total Laps: {overview.get('total_laps', 'Unknown')}")
        text.append(f"Total Drivers: {overview.get('total_drivers', 'Unknown')}")
        
        winner = overview.get('winner')
        if winner:
            text.append(f"Winner: {winner['name']} ({winner['driver']}) - {winner['team']}")
        
        # Key incidents
        incidents = self.analysis_results.get('incidents', [])
        text.append(f"\n## Key Incidents ({len(incidents)})")
        for incident in incidents:
            text.append(f"Lap {incident['lap']}: {incident['message']}")
            if 'telemetry_analysis' in incident and incident['telemetry_analysis']:
                for driver, data in incident['telemetry_analysis'].items():
                    if 'analysis' in data and 'anomalies' in data['analysis']:
                        for anomaly in data['analysis']['anomalies']:
                            text.append(f"  {driver}: {anomaly}")
        
        # Major position changes
        changes = self.analysis_results.get('major_position_changes', [])
        text.append(f"\n## Major Position Changes ({len(changes)})")
        for change in changes[:10]:  # Top 10
            text.append(f"{change['driver']} Lap {change['lap']}: {change['from_position']} → {change['to_position']} ({change['change']:+d})")
            if 'telemetry_comparison' in change and 'anomalies' in change['telemetry_comparison']:
                for anomaly in change['telemetry_comparison']['anomalies']:
                    text.append(f"  {anomaly}")
        
        # Track limits violations
        violations = self.analysis_results.get('track_limits_violations', [])
        text.append(f"\n## Track Limits Violations ({len(violations)})")
        for violation in violations:
            text.append(f"Lap {violation['lap']}: {violation['driver_abbreviation']} - {violation['message']}")
            if 'telemetry_analysis' in violation and 'analysis' in violation['telemetry_analysis']:
                analysis = violation['telemetry_analysis']['analysis']
                if 'anomalies' in analysis:
                    for anomaly in analysis['anomalies']:
                        text.append(f"  {anomaly}")
        
        # Commentary segments
        segments = self.analysis_results.get('commentary_segments', [])
        text.append(f"\n## Recommended Commentary Segments ({len(segments)})")
        for segment in segments:
            text.append(f"Priority {segment['priority']}: {segment['title']}")
            text.append(f"  {segment['description']}")
        
        return "\n".join(text)
    
    def print_summary(self) -> None:
        """Print analysis summary."""
        if not self.analysis_results:
            print("No analysis results available. Run generate_comprehensive_analysis() first.")
            return
        
        print("\n" + "="*60)
        print("F1 RACE ANALYSIS SUMMARY")
        print("="*60)
        
        overview = self.analysis_results.get('race_overview', {})
        winner = overview.get('winner')
        if winner:
            print(f"Winner: {winner['name']} ({winner['driver']}) - {winner['team']}")
        
        stats = self.analysis_results.get('statistics', {})
        print(f"\nStatistics:")
        print(f"  Total position changes: {stats.get('total_position_changes', 0)}")
        print(f"  Major changes (5+ positions): {stats.get('major_changes_5plus', 0)}")
        print(f"  Total incidents: {stats.get('total_incidents', 0)}")
        print(f"  Track limits violations: {stats.get('track_limits_violations', 0)}")
        print(f"  Yellow flag periods: {stats.get('yellow_flag_periods', 0)}")
        
        segments = self.analysis_results.get('commentary_segments', [])
        print(f"\nTop Commentary Segments:")
        for segment in segments[:5]:
            print(f"  {segment['priority']}. {segment['title']}")


def main():
    """Main function to run the race analyzer."""
    parser = argparse.ArgumentParser(description="Analyze F1 race data for interesting segments")
    parser.add_argument("--data_dir", required=True, help="Directory containing race data CSV files")
    parser.add_argument("--race", required=True, help="Name of the race to analyze")
    parser.add_argument("--output", default="./analysis_results", help="Output directory for results")
    parser.add_argument("--format", default="all", choices=["json", "txt", "all"], 
                       help="Output format")
    parser.add_argument("--summary", action="store_true", help="Print analysis summary")
    
    args = parser.parse_args()
    
    # Initialize analyzer
    analyzer = F1RaceAnalyzer(args.data_dir)
    
    # Load race data
    if not analyzer.load_race_data(args.race):
        print("Failed to load race data. Exiting.")
        sys.exit(1)
    
    # Generate analysis
    analyzer.generate_comprehensive_analysis()
    
    # Print summary if requested
    if args.summary:
        analyzer.print_summary()
    
    # Save results
    analyzer.save_analysis(output_dir=args.output, format=args.format)
    
    print(f"\nAnalysis complete! Check {args.output} for results.")


if __name__ == "__main__":
    main()
