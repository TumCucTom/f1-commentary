#!/usr/bin/env python3
"""
Example script for generating F1 commentary using Groq API

This script demonstrates how to use the commentary generator to create
engaging F1 commentary from race analysis data.
"""

import os
import json
from dotenv import load_dotenv
from commentary_generator import F1CommentaryGenerator


def example_generate_commentary():
    """Example of generating commentary from race data."""
    print("F1 Commentary Generator Example")
    print("=" * 50)
    
    # Load environment variables from .env file
    load_dotenv()
    
    # Check for API key
    api_key = os.getenv('GROQ_API_KEY')
    if not api_key:
        print("Error: GROQ_API_KEY not found in .env file")
        print("Please add your Groq API key to the .env file:")
        print("GROQ_API_KEY=your_api_key_here")
        return
    
    # Load race data
    try:
        with open('detailed_telemetry_analysis.json', 'r') as f:
            race_data = json.load(f)
        print("✓ Loaded race data")
    except FileNotFoundError:
        print("Error: detailed_telemetry_analysis.json not found")
        print("Please run the enhanced telemetry analysis first")
        return
    
    # Initialize generator
    generator = F1CommentaryGenerator(api_key)
    
    # Generate specific types of commentary
    print("\n1. Generating incident commentary...")
    incidents = race_data.get('incidents', [])
    if incidents:
        incident_commentary = generator.generate_incident_commentary(incidents[0])
        print(f"Incident Commentary: {incident_commentary['commentary']}")
    
    print("\n2. Generating position change commentary...")
    position_changes = race_data.get('major_position_changes', [])
    if position_changes:
        position_commentary = generator.generate_position_change_commentary(position_changes[0])
        print(f"Position Change Commentary: {position_commentary['commentary']}")
    
    print("\n3. Generating track limits commentary...")
    violations = race_data.get('track_limits_violations', [])
    if violations:
        violation_commentary = generator.generate_track_limits_commentary(violations[0])
        print(f"Track Limits Commentary: {violation_commentary['commentary']}")
    
    print("\n4. Generating race summary...")
    summary_commentary = generator.generate_race_summary_commentary(race_data)
    print(f"Race Summary: {summary_commentary['commentary']}")


def example_generate_full_commentary():
    """Example of generating full commentary set."""
    print("\n" + "=" * 50)
    print("GENERATING FULL COMMENTARY SET")
    print("=" * 50)
    
    # Load environment variables from .env file
    load_dotenv()
    
    # Check for API key
    api_key = os.getenv('GROQ_API_KEY')
    if not api_key:
        print("Error: GROQ_API_KEY not found in .env file")
        return
    
    # Load race data
    try:
        with open('detailed_telemetry_analysis.json', 'r') as f:
            race_data = json.load(f)
    except FileNotFoundError:
        print("Error: detailed_telemetry_analysis.json not found")
        return
    
    # Initialize generator
    generator = F1CommentaryGenerator(api_key)
    
    # Generate all commentary
    print("Generating comprehensive commentary...")
    commentaries = generator.process_race_data(race_data)
    
    # Save results
    output_data = {
        'race_info': {
            'data_file': 'detailed_telemetry_analysis.json',
            'model_used': 'llama-3.1-70b-versatile',
            'total_commentaries': len(commentaries)
        },
        'commentaries': commentaries
    }
    
    with open('example_commentary_output.json', 'w') as f:
        json.dump(output_data, f, indent=2, default=str)
    
    print(f"\n✓ Generated {len(commentaries)} commentary pieces")
    print("✓ Saved to example_commentary_output.json")
    
    # Display all commentaries
    print("\n" + "=" * 60)
    print("GENERATED COMMENTARIES")
    print("=" * 60)
    
    for i, commentary in enumerate(commentaries):
        print(f"\n{i+1}. {commentary['type'].upper()}:")
        print(f"   {commentary['commentary']}")
        print()


if __name__ == "__main__":
    try:
        example_generate_commentary()
        example_generate_full_commentary()
        
        print("\n" + "=" * 50)
        print("COMMENTARY GENERATION COMPLETE!")
        print("=" * 50)
        print("Check 'example_commentary_output.json' for all generated commentaries.")
        
    except Exception as e:
        print(f"Error: {e}")
        print("Make sure you have:")
        print("1. Set GROQ_API_KEY environment variable")
        print("2. Run the enhanced telemetry analysis first")
        print("3. Have detailed_telemetry_analysis.json in the current directory")
