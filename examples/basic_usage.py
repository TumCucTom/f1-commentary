#!/usr/bin/env python3
"""
Basic usage example for F1 Commentary package.

This example demonstrates how to use the F1 Commentary package to:
1. Collect F1 race data
2. Analyze the race
3. Generate commentary
4. Create visualizations
"""

import os
import sys
from pathlib import Path

# Add the src directory to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from f1_commentary import F1DataCollector, F1RaceAnalyzer, F1CommentaryGenerator
from f1_commentary.config import get_settings, APIKeyManager


def main():
    """Run the basic usage example."""
    print("F1 Commentary - Basic Usage Example")
    print("=" * 50)
    
    # Check API keys
    key_manager = APIKeyManager()
    if not key_manager.has_key('groq_api_key'):
        print("Warning: GROQ_API_KEY not found. Commentary generation will be skipped.")
        print("Set GROQ_API_KEY environment variable to enable commentary generation.")
    
    # Get settings
    settings = get_settings()
    print(f"Cache directory: {settings.cache_dir}")
    print(f"Output directory: {settings.output_dir}")
    
    # Example 1: Collect race data
    print("\n1. Collecting F1 race data...")
    try:
        collector = F1DataCollector()
        
        # Load a session (this will download data if not cached)
        if collector.load_session(2024, "Hungary", "R"):
            print("✓ Session loaded successfully")
            
            # Collect comprehensive data
            data = collector.get_comprehensive_data()
            print(f"✓ Collected data for {len(data)} data types")
            
            # Save data
            collector.save_data(output_dir="./example_output", format="json")
            print("✓ Data saved to ./example_output")
            
            # Print summary
            collector.print_summary()
        else:
            print("✗ Failed to load session")
            return 1
            
    except Exception as e:
        print(f"✗ Error collecting data: {e}")
        return 1
    
    # Example 2: Analyze race data
    print("\n2. Analyzing race data...")
    try:
        analyzer = F1RaceAnalyzer("./example_output")
        
        if analyzer.load_race_data("Hungary"):
            print("✓ Race data loaded successfully")
            
            # Generate comprehensive analysis
            results = analyzer.generate_comprehensive_analysis()
            print("✓ Analysis completed")
            
            # Save analysis
            analyzer.save_analysis(output_dir="./example_analysis", format="json")
            print("✓ Analysis saved to ./example_analysis")
            
            # Print summary
            analyzer.print_summary()
        else:
            print("✗ Failed to load race data")
            return 1
            
    except Exception as e:
        print(f"✗ Error analyzing data: {e}")
        return 1
    
    # Example 3: Generate commentary (if API key is available)
    if key_manager.has_key('groq_api_key'):
        print("\n3. Generating commentary...")
        try:
            generator = F1CommentaryGenerator(key_manager.get_groq_key())
            
            # Load analysis results
            import json
            analysis_files = list(Path("./example_analysis").glob("race_analysis_*.json"))
            if analysis_files:
                latest_analysis = max(analysis_files, key=lambda p: p.stat().st_mtime)
                
                with open(latest_analysis, 'r') as f:
                    race_data = json.load(f)
                
                # Generate commentary
                commentaries = generator.process_race_data(race_data)
                print(f"✓ Generated {len(commentaries)} commentary pieces")
                
                # Save commentary
                output_data = {
                    'race_info': {
                        'data_file': str(latest_analysis),
                        'total_commentaries': len(commentaries)
                    },
                    'commentaries': commentaries
                }
                
                with open("./example_commentary.json", 'w') as f:
                    json.dump(output_data, f, indent=2, default=str)
                
                print("✓ Commentary saved to ./example_commentary.json")
                
                # Print sample commentary
                if commentaries:
                    print("\nSample commentary:")
                    print(f"  {commentaries[0]['commentary']}")
            else:
                print("✗ No analysis files found")
                
        except Exception as e:
            print(f"✗ Error generating commentary: {e}")
    else:
        print("\n3. Skipping commentary generation (no API key)")
    
    # Example 4: Create visualization (simplified)
    print("\n4. Visualization example...")
    print("To create incident visualizations, use the CLI:")
    print("  f1-commentary visualize --year 2024 --race Hungary --driver1 VER --driver2 HAM --lap 63 --start-time '13:45:30' --duration 30")
    
    print("\n" + "=" * 50)
    print("Example completed successfully!")
    print("Check the following directories for output:")
    print("  - ./example_output (race data)")
    print("  - ./example_analysis (race analysis)")
    if key_manager.has_key('groq_api_key'):
        print("  - ./example_commentary.json (generated commentary)")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
