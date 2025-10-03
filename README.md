# F1 Race Data Collector

A comprehensive Python script that retrieves all available data about Formula 1 races using the FastF1 API.

## Features

- **Complete Race Data**: Retrieves all available data types for any F1 race
- **Multiple Data Formats**: Export to JSON, CSV, Excel, or all formats
- **Caching**: Built-in caching to speed up repeated data requests
- **Comprehensive Coverage**: Includes results, lap times, telemetry, weather, track status, and more
- **User-Friendly**: Command-line interface with helpful options

## Data Types Collected

- **Event Information**: Race details, location, dates, session info
- **Session Results**: Final standings and positions
- **Lap Data**: Detailed lap-by-lap information for all drivers
- **Telemetry Data**: Car telemetry (speed, RPM, gear, throttle, brake, etc.)
- **Weather Data**: Weather conditions during the session
- **Track Status**: Safety car periods, red flags, yellow flags
- **Session Status**: Session timing and status information
- **Race Control Messages**: Official race control communications
- **Driver Information**: Driver details, teams, numbers
- **Team Information**: Constructor details and information

## Installation

1. Install Python 3.8 or higher
2. Install required dependencies:

```bash
pip install -r requirements.txt
```

## Usage

### Basic Usage

```bash
# Get race data for 2023 Monaco Grand Prix
python f1_race_data.py --year 2023 --event "Monaco Grand Prix" --session R

# Get qualifying data for 2023 race 5 (Monaco)
python f1_race_data.py --year 2023 --race 5 --session Q

# Get practice session data
python f1_race_data.py --year 2023 --race 5 --session FP1
```

### Advanced Usage

```bash
# Save data in specific format
python f1_race_data.py --year 2023 --race 5 --session R --format json

# Specify custom output directory
python f1_race_data.py --year 2023 --race 5 --session R --output ./my_f1_data

# Get telemetry for specific driver only
python f1_race_data.py --year 2023 --race 5 --session R --driver VER

# Print summary and save data
python f1_race_data.py --year 2023 --race 5 --session R --summary

# Use custom cache directory
python f1_race_data.py --year 2023 --race 5 --session R --cache ./my_cache
```

### Command Line Options

- `--year`: Race year (required)
- `--race`: Race number (1-24) or event name
- `--event`: Event name (alternative to --race)
- `--session`: Session type (FP1, FP2, FP3, Q, R, S)
- `--output`: Output directory (default: ./f1_data_output)
- `--format`: Output format - json, csv, excel, or all (default: all)
- `--cache`: Cache directory (default: ./f1_cache)
- `--driver`: Specific driver for telemetry data
- `--summary`: Print data summary to console

### Session Types

- `FP1`: Free Practice 1
- `FP2`: Free Practice 2
- `FP3`: Free Practice 3
- `Q`: Qualifying
- `R`: Race
- `S`: Sprint (where applicable)

## Output Files

The script creates timestamped files in your specified output directory:

- **JSON**: Complete data in JSON format
- **CSV**: Individual CSV files for each data type
- **Excel**: Multi-sheet Excel file with all data

## Example Output Structure

```
f1_data_output/
├── Monaco Grand Prix_20231201_143022.json
├── Monaco Grand Prix_20231201_143022.xlsx
└── Monaco Grand Prix_20231201_143022_csv/
    ├── session_results.csv
    ├── lap_data.csv
    ├── weather_data.csv
    ├── track_status.csv
    └── ...
```

## Data Examples

### Event Information
```json
{
  "event_name": "Monaco Grand Prix",
  "location": "Monte Carlo",
  "country": "Monaco",
  "date": "2023-05-28",
  "session_name": "Race",
  "session_type": "Race"
}
```

### Lap Data
Contains detailed lap-by-lap information including:
- Lap times
- Sector times
- Pit stops
- Tire compounds
- Driver positions
- And much more

### Telemetry Data
High-resolution car telemetry including:
- Speed
- RPM
- Gear
- Throttle position
- Brake pressure
- DRS status
- And more

## Caching

The script automatically caches downloaded data to speed up subsequent requests. The cache directory can be customized with the `--cache` option.

## Error Handling

The script includes comprehensive error handling for:
- Invalid race years or numbers
- Network connectivity issues
- Missing data
- API rate limits

## Requirements

- Python 3.8+
- FastF1 library
- Pandas
- NumPy
- Matplotlib (for potential future visualizations)
- Seaborn (for potential future visualizations)

## Notes

- First-time data download may take several minutes due to the large amount of data
- Subsequent requests for the same race will be much faster due to caching
- Some historical races may have limited data availability
- The FastF1 API is free but has rate limits for very frequent requests

## Troubleshooting

1. **Import Error**: Make sure all dependencies are installed with `pip install -r requirements.txt`
2. **Network Issues**: Check your internet connection and try again
3. **Invalid Race**: Verify the year and race number/name are correct
4. **No Data**: Some sessions may not have all data types available

## Race Analyzer Tool

The project includes an advanced `race_analyzer.py` script that automatically analyzes F1 race data to identify interesting segments for commentary.

### Features

- **Automatic Incident Detection**: Finds collisions, track limits violations, and race control messages
- **Position Change Analysis**: Identifies major position changes and overtakes
- **Strategy Analysis**: Analyzes pit stop strategies and tire compounds
- **Commentary Segment Identification**: Automatically ranks the most interesting moments
- **Weather Impact Analysis**: Correlates weather conditions with race events
- **Multiple Output Formats**: JSON, text, and summary formats

### Usage

```bash
# Analyze a specific race
python race_analyzer.py --data_dir ./f1_data_output --race "Hungarian Grand Prix" --summary

# Save results to custom directory
python race_analyzer.py --data_dir ./f1_data_output --race "Monaco Grand Prix" --output ./monaco_analysis

# Generate only JSON output
python race_analyzer.py --data_dir ./f1_data_output --race "Silverstone" --format json
```

### Programmatic Usage

```python
from race_analyzer import F1RaceAnalyzer

# Initialize analyzer
analyzer = F1RaceAnalyzer("./f1_data_output")

# Load race data
analyzer.load_race_data("Hungarian Grand Prix")

# Generate analysis
results = analyzer.generate_comprehensive_analysis()

# Get specific analysis
incidents = analyzer.analyze_incidents()
position_changes = analyzer.analyze_position_changes(min_change=5)
commentary_segments = analyzer.identify_commentary_segments()

# Save results
analyzer.save_analysis(output_dir="./analysis", format="all")
```

### Analysis Output

The analyzer generates:

1. **Race Overview**: Winner, podium, basic statistics
2. **Incidents**: All collisions, track limits violations, steward decisions
3. **Position Changes**: Major position changes with lap times and reasons
4. **Pit Stop Strategies**: Complete strategy analysis for all drivers
5. **Weather Conditions**: Temperature, humidity, wind impact
6. **Commentary Segments**: Ranked list of most interesting moments

### Example Output

```
F1 RACE ANALYSIS SUMMARY
============================================================
Winner: Oscar Piastri (PIA) - McLaren

Statistics:
  Total position changes: 275
  Major changes (5+ positions): 15
  Total incidents: 5
  Track limits violations: 5
  Yellow flag periods: 1

Top Commentary Segments:
  1. Collision - Lap 63
  2. STR - -8 positions (Lap 15)
  3. RIC - -8 positions (Lap 8)
  4. HUL - -8 positions (Lap 30)
  5. Track Limits - Lap 35
```

## License

This script is provided as-is for educational and research purposes. Please respect the FastF1 API terms of service.
