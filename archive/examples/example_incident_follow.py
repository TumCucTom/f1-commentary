#!/usr/bin/env python3
"""
Example: F1 Race Incident Follow

This script demonstrates how to use the race incident follow functionality
to create visualizations of specific incidents that match up with commentary.

Usage:
    python example_incident_follow.py
"""

import subprocess
import os


def run_incident_follow_example():
    """Run an example of the incident follow functionality."""
    
    print("=== F1 Race Incident Follow Example ===\n")
    
    # Example: VER vs HAM collision on Lap 63 of Hungary 2024
    # This matches the collision mentioned in the commentary
    
    print("Creating visualization for VER vs HAM collision on Lap 63...")
    print("This matches the collision commentary from crofty_commentary_v3_text.txt")
    
    cmd = [
        'python', 'race_incident_follow.py',
        '--year', '2024',
        '--race', 'Hungary',
        '--driver1', 'VER',
        '--driver2', 'HAM',
        '--lap', '63',
        '--start_time', '13:45:30',  # Estimated time for lap 63
        '--duration', '30',  # 30 seconds of incident
        '--follow',  # Follow the cars
        '--road',  # Add track surface
        '--gif-seconds', '10'  # 10 second GIF
    ]
    
    try:
        print("Running command:")
        print(' '.join(cmd))
        print()
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        
        if result.returncode == 0:
            print("✅ Successfully created incident visualization!")
            print("Check for the generated GIF file in the current directory.")
        else:
            print("❌ Failed to create visualization")
            print(f"Error: {result.stderr}")
            
    except subprocess.TimeoutExpired:
        print("⏰ Command timed out")
    except Exception as e:
        print(f"❌ Error: {e}")


def run_automated_visualization_example():
    """Run the automated visualization generator."""
    
    print("\n=== Automated Incident Visualization Example ===\n")
    
    print("Generating visualizations for all incidents in the commentary...")
    
    cmd = [
        'python', 'generate_incident_visualizations.py',
        '--commentary', 'crofty_commentary_v3.json',
        '--race', 'Hungary',
        '--year', '2024',
        '--max-incidents', '3'  # Limit to 3 incidents for demo
    ]
    
    try:
        print("Running command:")
        print(' '.join(cmd))
        print()
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
        
        if result.returncode == 0:
            print("✅ Successfully generated incident visualizations!")
            print("Check the 'incident_visualizations' directory for GIF files.")
            print("Check 'incident_summary.md' for a summary document.")
        else:
            print("❌ Failed to generate visualizations")
            print(f"Error: {result.stderr}")
            
    except subprocess.TimeoutExpired:
        print("⏰ Command timed out")
    except Exception as e:
        print(f"❌ Error: {e}")


def main():
    """Main function to run examples."""
    
    print("F1 Race Incident Follow - Example Usage")
    print("=" * 50)
    
    # Check if required files exist
    if not os.path.exists('crofty_commentary_v3.json'):
        print("❌ crofty_commentary_v3.json not found")
        print("Please run the commentary generator first to create this file.")
        return
    
    if not os.path.exists('race_incident_follow.py'):
        print("❌ race_incident_follow.py not found")
        print("Please ensure the incident follow script is in the current directory.")
        return
    
    # Run examples
    print("\n1. Manual Incident Follow Example")
    run_incident_follow_example()
    
    print("\n2. Automated Visualization Example")
    run_automated_visualization_example()
    
    print("\n=== Example Complete ===")
    print("\nTo create your own incident visualizations:")
    print("1. Use race_incident_follow.py for specific incidents")
    print("2. Use generate_incident_visualizations.py for automated generation")
    print("3. Match the timing with your commentary data")


if __name__ == "__main__":
    main()




