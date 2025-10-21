#!/usr/bin/env python3
"""
Example usage of the F1 Race Data Collector

This script demonstrates how to use the F1RaceDataCollector class programmatically.
"""

from f1_race_data import F1RaceDataCollector


def example_basic_usage():
    """Basic example of collecting F1 race data."""
    print("=== Basic Usage Example ===")
    
    # Initialize the collector
    collector = F1RaceDataCollector(cache_dir="./example_cache")
    
    # Load a specific session (2023 Monaco Grand Prix Race)
    if collector.load_session(2023, "Monaco Grand Prix", "R"):
        # Get comprehensive data
        data = collector.get_comprehensive_data()
        
        # Print summary
        collector.print_summary()
        
        # Save data
        collector.save_data(output_dir="./example_output", format="json")
        
        print("Basic example completed!")
    else:
        print("Failed to load session")


def example_specific_data():
    """Example of getting specific data types."""
    print("\n=== Specific Data Example ===")
    
    collector = F1RaceDataCollector()
    
    if collector.load_session(2023, 5, "Q"):  # Monaco qualifying
        # Get only specific data types
        event_info = collector.get_event_info()
        results = collector.get_session_results()
        weather = collector.get_weather_data()
        
        print(f"Event: {event_info['event_name']}")
        print(f"Location: {event_info['location']}")
        print(f"Number of drivers: {len(results)}")
        print(f"Weather data points: {len(weather)}")
        
        # Get telemetry for a specific driver
        ver_telemetry = collector.get_telemetry_data("VER")
        if "VER" in ver_telemetry:
            print(f"Verstappen telemetry points: {len(ver_telemetry['VER'])}")
        
        print("Specific data example completed!")


def example_driver_analysis():
    """Example of analyzing driver performance."""
    print("\n=== Driver Analysis Example ===")
    
    collector = F1RaceDataCollector()
    
    if collector.load_session(2023, 5, "R"):  # Monaco race
        # Get lap data
        laps = collector.get_lap_data()
        
        if not laps.empty:
            # Find fastest lap
            fastest_lap = laps.loc[laps['LapTime'].idxmin()]
            print(f"Fastest lap: {fastest_lap['Driver']} - {fastest_lap['LapTime']}")
            
            # Get driver info
            driver_info = collector.get_driver_info()
            fastest_driver = fastest_lap['Driver']
            if fastest_driver in driver_info:
                driver_details = driver_info[fastest_driver]
                print(f"Driver: {driver_details['full_name']} ({driver_details['team']})")
        
        print("Driver analysis example completed!")


def example_weather_analysis():
    """Example of analyzing weather conditions."""
    print("\n=== Weather Analysis Example ===")
    
    collector = F1RaceDataCollector()
    
    if collector.load_session(2023, 5, "R"):  # Monaco race
        weather = collector.get_weather_data()
        
        if not weather.empty:
            print(f"Weather data collected for {len(weather)} time points")
            print(f"Temperature range: {weather['AirTemp'].min():.1f}°C - {weather['AirTemp'].max():.1f}°C")
            print(f"Track temperature range: {weather['TrackTemp'].min():.1f}°C - {weather['TrackTemp'].max():.1f}°C")
            
            # Check for rain
            if 'Rainfall' in weather.columns:
                rain_periods = weather[weather['Rainfall'] > 0]
                if not rain_periods.empty:
                    print(f"Rain detected at {len(rain_periods)} time points")
                else:
                    print("No rain detected during the session")
        
        print("Weather analysis example completed!")


def example_telemetry_analysis():
    """Example of analyzing telemetry data."""
    print("\n=== Telemetry Analysis Example ===")
    
    collector = F1RaceDataCollector()
    
    if collector.load_session(2023, 5, "R"):  # Monaco race
        # Get telemetry for top 3 drivers
        results = collector.get_session_results()
        if not results.empty:
            top_3_drivers = results.head(3)['Abbreviation'].tolist()
            
            for driver in top_3_drivers:
                telemetry = collector.get_telemetry_data(driver)
                if driver in telemetry:
                    tel_data = telemetry[driver]
                    if not tel_data.empty:
                        max_speed = tel_data['Speed'].max()
                        avg_speed = tel_data['Speed'].mean()
                        print(f"{driver}: Max speed {max_speed:.1f} km/h, Avg speed {avg_speed:.1f} km/h")
        
        print("Telemetry analysis example completed!")


if __name__ == "__main__":
    print("F1 Race Data Collector - Example Usage")
    print("=" * 50)
    
    try:
        # Run examples
        example_basic_usage()
        example_specific_data()
        example_driver_analysis()
        example_weather_analysis()
        example_telemetry_analysis()
        
        print("\n" + "=" * 50)
        print("All examples completed successfully!")
        print("Check the 'example_output' directory for saved data files.")
        
    except Exception as e:
        print(f"Error running examples: {e}")
        print("Make sure you have a stable internet connection and the required dependencies installed.")

