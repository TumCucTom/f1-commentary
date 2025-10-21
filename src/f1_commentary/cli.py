"""
Command-line interface for F1 Commentary package.
"""

import argparse
import sys
from pathlib import Path
from typing import Optional

from .config import get_settings, APIKeyManager
from .utils.logging import setup_logging
from .data import F1DataCollector
from .analysis import F1RaceAnalyzer
from .commentary import F1CommentaryGenerator
from .visualization import F1IncidentVisualizer


def create_parser() -> argparse.ArgumentParser:
    """Create the main argument parser."""
    parser = argparse.ArgumentParser(
        description="F1 Commentary - Comprehensive F1 race analysis and commentary generation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Collect race data
  f1-commentary collect --year 2024 --race "Hungary" --session R
  
  # Analyze race data
  f1-commentary analyze --data-dir ./f1_data_output --race "Hungary"
  
  # Generate commentary
  f1-commentary comment --data-file analysis_results/race_analysis_20240101_120000.json
  
  # Create incident visualization
  f1-commentary visualize --year 2024 --race "Hungary" --driver1 VER --driver2 HAM --lap 63 --start-time "13:45:30" --duration 30
  
  # Full pipeline
  f1-commentary pipeline --year 2024 --race "Hungary" --session R
        """
    )
    
    # Global options
    parser.add_argument('--verbose', '-v', action='store_true', help='Enable verbose logging')
    parser.add_argument('--log-file', help='Log file path')
    parser.add_argument('--config', help='Configuration file path')
    
    # Subcommands
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Collect command
    collect_parser = subparsers.add_parser('collect', help='Collect F1 race data')
    collect_parser.add_argument('--year', type=int, required=True, help='Race year')
    collect_parser.add_argument('--race', help='Race number (1-24) or event name')
    collect_parser.add_argument('--event', help='Event name (alternative to --race)')
    collect_parser.add_argument('--session', default='R', help='Session type (FP1, FP2, FP3, Q, R, S)')
    collect_parser.add_argument('--output', help='Output directory')
    collect_parser.add_argument('--format', default='all', choices=['json', 'csv', 'excel', 'all'], help='Output format')
    collect_parser.add_argument('--cache', help='Cache directory')
    collect_parser.add_argument('--driver', help='Specific driver for telemetry')
    collect_parser.add_argument('--summary', action='store_true', help='Print data summary')
    
    # Analyze command
    analyze_parser = subparsers.add_parser('analyze', help='Analyze F1 race data')
    analyze_parser.add_argument('--data-dir', required=True, help='Directory containing race data')
    analyze_parser.add_argument('--race', required=True, help='Name of the race to analyze')
    analyze_parser.add_argument('--output', help='Output directory for results')
    analyze_parser.add_argument('--format', default='all', choices=['json', 'txt', 'all'], help='Output format')
    analyze_parser.add_argument('--summary', action='store_true', help='Print analysis summary')
    
    # Comment command
    comment_parser = subparsers.add_parser('comment', help='Generate F1 commentary')
    comment_parser.add_argument('--data-file', required=True, help='JSON file containing race analysis data')
    comment_parser.add_argument('--output', default='commentary_output.json', help='Output file for generated commentary')
    comment_parser.add_argument('--api-key', help='Groq API key')
    comment_parser.add_argument('--model', default='llama-3.1-8b-instant', help='Groq model to use')
    
    # Visualize command
    visualize_parser = subparsers.add_parser('visualize', help='Create incident visualizations')
    visualize_parser.add_argument('--year', type=int, required=True, help='Year of the race')
    visualize_parser.add_argument('--race', required=True, help='Name of the Grand Prix')
    visualize_parser.add_argument('--driver1', required=True, help='First driver code')
    visualize_parser.add_argument('--driver2', required=True, help='Second driver code')
    visualize_parser.add_argument('--lap', type=int, required=True, help='Lap number')
    visualize_parser.add_argument('--start-time', required=True, help='Start time (HH:MM:SS)')
    visualize_parser.add_argument('--duration', type=int, required=True, help='Duration in seconds')
    visualize_parser.add_argument('--follow', action='store_true', help='Enable camera follow')
    visualize_parser.add_argument('--follow-window', type=float, default=200.0, help='Follow window size')
    visualize_parser.add_argument('--gif-seconds', type=float, help='Target GIF duration')
    visualize_parser.add_argument('--road', action='store_true', help='Add realistic track surface')
    
    # Pipeline command
    pipeline_parser = subparsers.add_parser('pipeline', help='Run full analysis pipeline')
    pipeline_parser.add_argument('--year', type=int, required=True, help='Race year')
    pipeline_parser.add_argument('--race', help='Race number or event name')
    pipeline_parser.add_argument('--event', help='Event name (alternative to --race)')
    pipeline_parser.add_argument('--session', default='R', help='Session type')
    pipeline_parser.add_argument('--output-dir', help='Base output directory')
    pipeline_parser.add_argument('--skip-collect', action='store_true', help='Skip data collection')
    pipeline_parser.add_argument('--skip-analyze', action='store_true', help='Skip analysis')
    pipeline_parser.add_argument('--skip-comment', action='store_true', help='Skip commentary generation')
    pipeline_parser.add_argument('--skip-visualize', action='store_true', help='Skip visualization')
    
    # Status command
    status_parser = subparsers.add_parser('status', help='Check system status')
    
    return parser


def handle_collect(args) -> int:
    """Handle the collect command."""
    try:
        # Determine race identifier
        race_identifier = args.race or args.event
        if not race_identifier:
            print("Error: Must specify either --race or --event")
            return 1
        
        # Initialize collector
        collector = F1DataCollector(cache_dir=args.cache)
        
        # Load session
        if not collector.load_session(args.year, race_identifier, args.session):
            print("Failed to load session. Exiting.")
            return 1
        
        # Collect data
        data = collector.get_comprehensive_data()
        
        # Print summary if requested
        if args.summary:
            collector.print_summary()
        
        # Save data
        collector.save_data(output_dir=args.output, format=args.format)
        
        print(f"Data collection complete! Check {args.output or './f1_data_output'} for output files.")
        return 0
        
    except Exception as e:
        print(f"Error during data collection: {e}")
        return 1


def handle_analyze(args) -> int:
    """Handle the analyze command."""
    try:
        # Initialize analyzer
        analyzer = F1RaceAnalyzer(args.data_dir)
        
        # Load race data
        if not analyzer.load_race_data(args.race):
            print("Failed to load race data. Exiting.")
            return 1
        
        # Generate analysis
        analyzer.generate_comprehensive_analysis()
        
        # Print summary if requested
        if args.summary:
            analyzer.print_summary()
        
        # Save results
        analyzer.save_analysis(output_dir=args.output, format=args.format)
        
        print(f"Analysis complete! Check {args.output or './analysis_results'} for results.")
        return 0
        
    except Exception as e:
        print(f"Error during analysis: {e}")
        return 1


def handle_comment(args) -> int:
    """Handle the comment command."""
    try:
        # Check API key
        api_key = args.api_key
        if not api_key:
            key_manager = APIKeyManager()
            api_key = key_manager.get_groq_key()
        
        if not api_key:
            print("Error: Groq API key required. Set GROQ_API_KEY environment variable or use --api-key")
            return 1
        
        # Initialize generator
        generator = F1CommentaryGenerator(api_key, args.model)
        
        # Load race data
        import json
        with open(args.data_file, 'r') as f:
            race_data = json.load(f)
        
        # Generate commentary
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
        
        print(f"Commentary generation complete! Generated {len(commentaries)} commentary pieces.")
        print(f"Results saved to {args.output}")
        return 0
        
    except Exception as e:
        print(f"Error during commentary generation: {e}")
        return 1


def handle_visualize(args) -> int:
    """Handle the visualize command."""
    try:
        # Convert driver codes to uppercase
        driver1 = args.driver1.upper()
        driver2 = args.driver2.upper()
        
        # Get incident position data
        from .visualization.incident_visualizer import get_race_incident_data, create_incident_animation
        
        data1, data2 = get_race_incident_data(
            args.year, args.race, driver1, driver2, 
            args.lap, args.start_time, args.duration
        )
        
        # Create animation
        if data1 is not None and data2 is not None:
            create_incident_animation(
                data1, data2, driver1, driver2, 
                args.year, args.race, args.lap, args.start_time, args.duration,
                follow=args.follow, window_size=args.follow_window,
                gif_seconds=args.gif_seconds, road=args.road
            )
            print("Visualization complete!")
            return 0
        else:
            print("Failed to retrieve incident data.")
            return 1
            
    except Exception as e:
        print(f"Error during visualization: {e}")
        return 1


def handle_pipeline(args) -> int:
    """Handle the pipeline command."""
    try:
        # Determine race identifier
        race_identifier = args.race or args.event
        if not race_identifier:
            print("Error: Must specify either --race or --event")
            return 1
        
        # Set up output directory
        output_dir = args.output_dir or f"./pipeline_output_{args.year}_{race_identifier.replace(' ', '_')}"
        
        print(f"Running full pipeline for {args.year} {race_identifier}")
        print(f"Output directory: {output_dir}")
        
        # Step 1: Collect data (if not skipped)
        if not args.skip_collect:
            print("\n=== Step 1: Collecting Race Data ===")
            collect_args = argparse.Namespace(
                year=args.year,
                race=args.race,
                event=args.event,
                session=args.session,
                output=f"{output_dir}/data",
                format='all',
                cache=None,
                driver=None,
                summary=True
            )
            if handle_collect(collect_args) != 0:
                return 1
        
        # Step 2: Analyze data (if not skipped)
        if not args.skip_analyze:
            print("\n=== Step 2: Analyzing Race Data ===")
            analyze_args = argparse.Namespace(
                data_dir=f"{output_dir}/data",
                race=race_identifier,
                output=f"{output_dir}/analysis",
                format='all',
                summary=True
            )
            if handle_analyze(analyze_args) != 0:
                return 1
        
        # Step 3: Generate commentary (if not skipped)
        if not args.skip_comment:
            print("\n=== Step 3: Generating Commentary ===")
            # Find the most recent analysis file
            analysis_dir = Path(f"{output_dir}/analysis")
            analysis_files = list(analysis_dir.glob("race_analysis_*.json"))
            if analysis_files:
                latest_analysis = max(analysis_files, key=lambda p: p.stat().st_mtime)
                comment_args = argparse.Namespace(
                    data_file=str(latest_analysis),
                    output=f"{output_dir}/commentary.json",
                    api_key=None,
                    model='llama-3.1-8b-instant'
                )
                if handle_comment(comment_args) != 0:
                    return 1
            else:
                print("Warning: No analysis files found, skipping commentary generation")
        
        # Step 4: Create visualizations (if not skipped)
        if not args.skip_visualize:
            print("\n=== Step 4: Creating Visualizations ===")
            print("Note: Visualization requires specific incident parameters")
            print("Use the 'visualize' command for specific incidents")
        
        print(f"\nPipeline complete! Check {output_dir} for all results.")
        return 0
        
    except Exception as e:
        print(f"Error during pipeline execution: {e}")
        return 1


def handle_status(args) -> int:
    """Handle the status command."""
    try:
        print("F1 Commentary System Status")
        print("=" * 40)
        
        # Check API keys
        key_manager = APIKeyManager()
        key_manager.print_status()
        
        # Check settings
        settings = get_settings()
        print(f"\nConfiguration:")
        print(f"  Cache directory: {settings.cache_dir}")
        print(f"  Output directory: {settings.output_dir}")
        print(f"  Analysis directory: {settings.analysis_dir}")
        print(f"  Visualization directory: {settings.visualization_dir}")
        
        # Check directories
        print(f"\nDirectories:")
        for name, path in [
            ("Cache", settings.cache_dir),
            ("Output", settings.output_dir),
            ("Analysis", settings.analysis_dir),
            ("Visualization", settings.visualization_dir)
        ]:
            exists = path.exists()
            status = "✓" if exists else "✗"
            print(f"  {status} {name}: {path}")
        
        return 0
        
    except Exception as e:
        print(f"Error checking status: {e}")
        return 1


def main() -> int:
    """Main entry point."""
    parser = create_parser()
    args = parser.parse_args()
    
    # Set up logging
    setup_logging(
        level='DEBUG' if args.verbose else 'INFO',
        log_file=Path(args.log_file) if args.log_file else None
    )
    
    # Handle commands
    if args.command == 'collect':
        return handle_collect(args)
    elif args.command == 'analyze':
        return handle_analyze(args)
    elif args.command == 'comment':
        return handle_comment(args)
    elif args.command == 'visualize':
        return handle_visualize(args)
    elif args.command == 'pipeline':
        return handle_pipeline(args)
    elif args.command == 'status':
        return handle_status(args)
    else:
        parser.print_help()
        return 1


if __name__ == '__main__':
    sys.exit(main())
