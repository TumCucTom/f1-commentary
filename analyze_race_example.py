#!/usr/bin/env python3
"""
Example usage of the F1 Race Analyzer

This script demonstrates how to use the F1RaceAnalyzer class programmatically.
"""

from race_analyzer import F1RaceAnalyzer


def example_analyze_hungary_2024():
    """Example: Analyze Hungary 2024 race."""
    print("=== Analyzing Hungary 2024 Race ===")
    
    # Initialize analyzer
    analyzer = F1RaceAnalyzer("./f1_data_output")
    
    # Load race data
    if analyzer.load_race_data("Hungarian Grand Prix"):
        # Generate comprehensive analysis
        results = analyzer.generate_comprehensive_analysis()
        
        # Print summary
        analyzer.print_summary()
        
        # Save results
        analyzer.save_analysis(output_dir="./hungary_analysis", format="all")
        
        # Access specific analysis results
        print(f"\nDetailed Results:")
        print(f"  - {len(results['incidents'])} incidents found")
        print(f"  - {len(results['major_position_changes'])} major position changes")
        print(f"  - {len(results['commentary_segments'])} commentary segments identified")
        
        # Show top incidents
        print(f"\nTop Incidents:")
        for incident in results['incidents'][:3]:
            print(f"  Lap {incident['lap']}: {incident['message']}")
        
        print("Analysis complete!")
    else:
        print("Failed to load race data")


def example_analyze_specific_segments():
    """Example: Analyze specific aspects of a race."""
    print("\n=== Analyzing Specific Race Segments ===")
    
    analyzer = F1RaceAnalyzer("./f1_data_output")
    
    if analyzer.load_race_data("Hungarian Grand Prix"):
        # Analyze only incidents
        incidents = analyzer.analyze_incidents()
        print(f"Found {len(incidents)} incidents:")
        for incident in incidents:
            print(f"  Lap {incident['lap']}: {incident['message']}")
        
        # Analyze only major position changes
        position_changes = analyzer.analyze_position_changes(min_change=5)
        print(f"\nFound {len(position_changes)} major position changes:")
        for change in position_changes[:5]:
            print(f"  {change['driver']} Lap {change['lap']}: {change['from_position']} → {change['to_position']} ({change['change']:+d})")
        
        # Analyze pit stop strategies
        strategies = analyzer.analyze_pit_stop_strategies()
        print(f"\nPit stop strategies for top teams:")
        for driver in ['PIA', 'NOR', 'VER', 'HAM']:
            if driver in strategies:
                print(f"  {driver}: {len(strategies[driver])} pit stops")
                for pit in strategies[driver]:
                    print(f"    Lap {pit['lap']}: {pit['compound']} tires")


def example_identify_commentary_segments():
    """Example: Identify the best segments for commentary."""
    print("\n=== Identifying Commentary Segments ===")
    
    analyzer = F1RaceAnalyzer("./f1_data_output")
    
    if analyzer.load_race_data("Hungarian Grand Prix"):
        # Get commentary segments
        segments = analyzer.identify_commentary_segments()
        
        print(f"Found {len(segments)} commentary segments:")
        for segment in segments:
            print(f"\nPriority {segment['priority']}: {segment['title']}")
            print(f"  Type: {segment['type']}")
            print(f"  Lap: {segment['lap']}")
            print(f"  Description: {segment['description']}")
            print(f"  Data points: {', '.join(segment['data_points'])}")


if __name__ == "__main__":
    print("F1 Race Analyzer - Example Usage")
    print("=" * 50)
    
    try:
        # Run examples
        example_analyze_hungary_2024()
        example_analyze_specific_segments()
        example_identify_commentary_segments()
        
        print("\n" + "=" * 50)
        print("All examples completed successfully!")
        
    except Exception as e:
        print(f"Error running examples: {e}")
        print("Make sure you have race data in the f1_data_output directory.")
