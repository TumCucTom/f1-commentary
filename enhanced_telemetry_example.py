#!/usr/bin/env python3
"""
Enhanced Telemetry Analysis Example

This script demonstrates the enhanced race analyzer with detailed telemetry data
for incidents, crashes, position changes, and track limits violations.
"""

from race_analyzer import F1RaceAnalyzer
import json


def analyze_verstappen_incidents():
    """Analyze Verstappen's incidents with detailed telemetry."""
    print("=== VERSTAPPEN INCIDENTS TELEMETRY ANALYSIS ===")
    
    analyzer = F1RaceAnalyzer("./f1_data_output")
    if analyzer.load_race_data("Hungarian Grand Prix"):
        incidents = analyzer.analyze_incidents()
        
        # Find Verstappen incidents
        ver_incidents = [inc for inc in incidents if 'VER' in inc.get('drivers', []) or '1' in inc.get('drivers', [])]
        
        for incident in ver_incidents:
            print(f"\nLap {incident['lap']}: {incident['message']}")
            print(f"Steward Action: {incident['steward_action']}")
            
            if 'telemetry_analysis' in incident and incident['telemetry_analysis']:
                for driver, telemetry in incident['telemetry_analysis'].items():
                    print(f"\n{driver} Telemetry Analysis:")
                    
                    # Show lap-by-lap data
                    if 'lap_data' in telemetry:
                        print("  Lap-by-lap data:")
                        for lap_key, lap_data in telemetry['lap_data'].items():
                            print(f"    {lap_key}:")
                            print(f"      Lap time: {lap_data['lap_time']}")
                            print(f"      Position: {lap_data['position']}")
                            print(f"      Speed FL: {lap_data['speed_fl']} km/h")
                            print(f"      Compound: {lap_data['compound']}")
                            print(f"      Tire life: {lap_data['tyre_life']} laps")
                    
                    # Show analysis
                    if 'analysis' in telemetry:
                        analysis = telemetry['analysis']
                        print("  Analysis:")
                        
                        if 'speed_analysis' in analysis:
                            speed_analysis = analysis['speed_analysis']
                            print(f"    Speed range: {speed_analysis.get('min_speed', 'N/A')} - {speed_analysis.get('max_speed', 'N/A')} km/h")
                            print(f"    Speed variance: {speed_analysis.get('speed_variance', 'N/A')} km/h")
                        
                        if 'anomalies' in analysis:
                            print(f"    Anomalies: {analysis['anomalies']}")


def analyze_major_position_changes():
    """Analyze major position changes with telemetry comparison."""
    print("\n\n=== MAJOR POSITION CHANGES TELEMETRY ANALYSIS ===")
    
    analyzer = F1RaceAnalyzer("./f1_data_output")
    if analyzer.load_race_data("Hungarian Grand Prix"):
        position_changes = analyzer.analyze_position_changes(min_change=5)
        
        print(f"Found {len(position_changes)} major position changes (5+ positions)")
        
        for change in position_changes[:5]:  # Top 5
            print(f"\n{change['driver']} Lap {change['lap']}: {change['from_position']} → {change['to_position']} ({change['change']:+d} positions)")
            print(f"  Lap time: {change['lap_time']}")
            print(f"  Previous lap time: {change['prev_lap_time']}")
            print(f"  Compound: {change['compound']}")
            print(f"  Tire life: {change['tyre_life']} laps")
            
            if 'telemetry_comparison' in change:
                comparison = change['telemetry_comparison']
                print("  Telemetry Comparison:")
                print(f"    Lap time change: {comparison['lap_time_change']}")
                
                if 'speed_changes' in comparison:
                    print("    Speed changes:")
                    for speed_field, change_value in comparison['speed_changes'].items():
                        print(f"      {speed_field}: {change_value}")
                
                if 'sector_changes' in comparison:
                    print("    Sector changes:")
                    for sector_field, change_value in comparison['sector_changes'].items():
                        print(f"      {sector_field}: {change_value}")
                
                if 'tire_changes' in comparison:
                    print("    Tire changes:")
                    for tire_field, change_value in comparison['tire_changes'].items():
                        print(f"      {tire_field}: {change_value}")
                
                if 'anomalies' in comparison:
                    print(f"    Anomalies: {comparison['anomalies']}")


def analyze_track_limits_violations():
    """Analyze track limits violations with telemetry data."""
    print("\n\n=== TRACK LIMITS VIOLATIONS TELEMETRY ANALYSIS ===")
    
    analyzer = F1RaceAnalyzer("./f1_data_output")
    if analyzer.load_race_data("Hungarian Grand Prix"):
        violations = analyzer.analyze_track_limits_violations()
        
        print(f"Found {len(violations)} track limits violations")
        
        for violation in violations:
            print(f"\nLap {violation['lap']}: {violation['driver_abbreviation']} - {violation['message']}")
            print(f"  Turn: {violation['turn']}")
            print(f"  Deleted time: {violation['deleted_time']}")
            
            if 'telemetry_analysis' in violation and violation['telemetry_analysis']:
                telemetry = violation['telemetry_analysis']
                
                if 'lap_data' in telemetry:
                    print("  Lap data around violation:")
                    for lap_key, lap_data in telemetry['lap_data'].items():
                        print(f"    {lap_key}:")
                        print(f"      Lap time: {lap_data['lap_time']}")
                        print(f"      Speed FL: {lap_data['speed_fl']} km/h")
                        print(f"      Sector times: {lap_data['sector1_time']}, {lap_data['sector2_time']}, {lap_data['sector3_time']}")
                
                if 'analysis' in telemetry:
                    analysis = telemetry['analysis']
                    if 'speed_analysis' in analysis:
                        speed_analysis = analysis['speed_analysis']
                        print(f"  Speed analysis: {speed_analysis}")
                    
                    if 'anomalies' in analysis:
                        print(f"  Anomalies: {analysis['anomalies']}")


def analyze_collision_telemetry():
    """Analyze the VER vs HAM collision in detail."""
    print("\n\n=== VER vs HAM COLLISION DETAILED ANALYSIS ===")
    
    analyzer = F1RaceAnalyzer("./f1_data_output")
    if analyzer.load_race_data("Hungarian Grand Prix"):
        incidents = analyzer.analyze_incidents()
        
        # Find the collision
        collision = None
        for incident in incidents:
            if 'COLLISION' in incident['message'] and 'VER' in incident['message'] and 'HAM' in incident['message']:
                collision = incident
                break
        
        if collision:
            print(f"Collision on Lap {collision['lap']}: {collision['message']}")
            print(f"Steward Action: {collision['steward_action']}")
            
            if 'telemetry_analysis' in collision:
                for driver, telemetry in collision['telemetry_analysis'].items():
                    print(f"\n{driver} Collision Analysis:")
                    
                    # Show detailed lap data
                    if 'lap_data' in telemetry:
                        print("  Detailed lap data:")
                        for lap_key, lap_data in telemetry['lap_data'].items():
                            print(f"    {lap_key}:")
                            print(f"      Position: {lap_data['position']}")
                            print(f"      Lap time: {lap_data['lap_time']}")
                            print(f"      Speed I1: {lap_data['speed_i1']} km/h")
                            print(f"      Speed I2: {lap_data['speed_i2']} km/h")
                            print(f"      Speed FL: {lap_data['speed_fl']} km/h")
                            print(f"      Speed ST: {lap_data['speed_st']} km/h")
                            print(f"      Sector 1: {lap_data['sector1_time']}")
                            print(f"      Sector 2: {lap_data['sector2_time']}")
                            print(f"      Sector 3: {lap_data['sector3_time']}")
                            print(f"      Compound: {lap_data['compound']}")
                            print(f"      Tire life: {lap_data['tyre_life']} laps")
                            print(f"      Personal best: {lap_data['is_personal_best']}")
                    
                    # Show analysis
                    if 'analysis' in telemetry:
                        analysis = telemetry['analysis']
                        print("  Analysis:")
                        
                        if 'speed_analysis' in analysis:
                            speed_analysis = analysis['speed_analysis']
                            print(f"    Speed range: {speed_analysis.get('min_speed', 'N/A')} - {speed_analysis.get('max_speed', 'N/A')} km/h")
                            print(f"    Speed variance: {speed_analysis.get('speed_variance', 'N/A')} km/h")
                            print(f"    Incident lap speed: {speed_analysis.get('incident_lap_speed', 'N/A')} km/h")
                        
                        if 'position_analysis' in analysis:
                            pos_analysis = analysis['position_analysis']
                            print(f"    Position range: {pos_analysis.get('position_range', 'N/A')}")
                            print(f"    Position change: {pos_analysis.get('position_change', 'N/A')}")
                            print(f"    Incident lap position: {pos_analysis.get('incident_lap_position', 'N/A')}")
                        
                        if 'tire_analysis' in analysis:
                            tire_analysis = analysis['tire_analysis']
                            print(f"    Compounds used: {tire_analysis.get('compounds_used', 'N/A')}")
                            print(f"    Tire age at incident: {tire_analysis.get('tire_age_at_incident', 'N/A')} laps")
                        
                        if 'anomalies' in analysis:
                            print(f"    Anomalies: {analysis['anomalies']}")
        else:
            print("Collision not found in analysis")


def save_detailed_analysis():
    """Save detailed analysis to JSON file."""
    print("\n\n=== SAVING DETAILED ANALYSIS ===")
    
    analyzer = F1RaceAnalyzer("./f1_data_output")
    if analyzer.load_race_data("Hungarian Grand Prix"):
        # Generate comprehensive analysis
        results = analyzer.generate_comprehensive_analysis()
        
        # Save with detailed telemetry
        with open('detailed_telemetry_analysis.json', 'w') as f:
            json.dump(results, f, indent=2, default=str)
        
        print("Detailed telemetry analysis saved to 'detailed_telemetry_analysis.json'")
        print(f"Analysis includes:")
        print(f"  - {len(results['incidents'])} incidents with telemetry")
        print(f"  - {len(results['major_position_changes'])} position changes with telemetry")
        print(f"  - {len(results['track_limits_violations'])} track limits violations with telemetry")
        print(f"  - {len(results['commentary_segments'])} commentary segments")


if __name__ == "__main__":
    print("Enhanced F1 Telemetry Analysis")
    print("=" * 50)
    
    try:
        # Run all analysis examples
        analyze_verstappen_incidents()
        analyze_major_position_changes()
        analyze_track_limits_violations()
        analyze_collision_telemetry()
        save_detailed_analysis()
        
        print("\n" + "=" * 50)
        print("Enhanced telemetry analysis complete!")
        print("Check 'detailed_telemetry_analysis.json' for complete data.")
        
    except Exception as e:
        print(f"Error running enhanced analysis: {e}")
        print("Make sure you have race data in the f1_data_output directory.")
