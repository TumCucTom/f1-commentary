# F1 Race Incident Follow - Visualizing Commentary Moments

This system allows you to create animated visualizations of specific incidents during F1 races, perfectly matching up with your commentary to show what actually happened.

## 🎯 What This Does

- **Follows two drivers** during a specific part of a specific lap
- **Matches timing** with your commentary data
- **Creates animated GIFs** showing the incident as it unfolds
- **Uses realistic track layouts** and car images
- **Supports follow camera** for close-up action

## 📁 Files Created

- `race_incident_follow.py` - Main script for creating incident visualizations
- `generate_incident_visualizations.py` - Automated generator from commentary data
- `example_incident_follow.py` - Example usage script

## 🚀 Quick Start

### 1. Manual Incident Visualization

Create a visualization for a specific incident:

```bash
python race_incident_follow.py \
  --year 2024 \
  --race "Hungary" \
  --driver1 "VER" \
  --driver2 "HAM" \
  --lap 63 \
  --start_time "13:45:30" \
  --duration 30 \
  --follow \
  --road
```

### 2. Automated Generation from Commentary

Generate visualizations for all incidents in your commentary:

```bash
python generate_incident_visualizations.py \
  --commentary crofty_commentary_v3.json \
  --race "Hungary" \
  --year 2024 \
  --max-incidents 5
```

### 3. Run Example

```bash
python example_incident_follow.py
```

## 📋 Command Line Options

### race_incident_follow.py

**Required:**
- `--year`: Year of the race (e.g., 2024)
- `--race`: Race name (e.g., "Hungary", "Monaco")
- `--driver1`: First driver code (e.g., "VER", "HAM")
- `--driver2`: Second driver code
- `--lap`: Lap number where incident occurred
- `--start_time`: Start time in HH:MM:SS format (race time)
- `--duration`: Duration in seconds to capture

**Optional:**
- `--follow`: Enable camera follow (keeps cars centered)
- `--follow-window`: Follow window size in meters (default: 200)
- `--road`: Add realistic track surface
- `--gif-seconds`: Target GIF duration (auto-adjusts fps)

### generate_incident_visualizations.py

**Required:**
- `--commentary`: Path to commentary JSON file
- `--race`: Race name
- `--year`: Year of the race

**Optional:**
- `--max-incidents`: Maximum incidents to visualize (default: 5)
- `--output-dir`: Output directory (default: incident_visualizations)
- `--race-start-time`: Race start time (default: 13:00:00)

## 🎬 Output

### Generated Files

- **GIF animations**: `commentary_segment_{lap}_{year}_{race}_{driver1}_vs_{driver2}_animated.gif`
- **Summary document**: `incident_summary.md` (with automated generation)
- **Visualization directory**: `incident_visualizations/` (with automated generation)

### Example Output Structure

```
incident_visualizations/
├── commentary_segment_2_2024_Hungarian_Grand_Prix_VER_vs_HAM_animated.gif
├── commentary_segment_63_2024_Hungarian_Grand_Prix_VER_vs_HAM_animated.gif
└── ...

incident_summary.md
```

## 🔧 How It Works

### 1. Time Matching

The system matches commentary incidents with race telemetry by:
- **Lap number**: Directly from commentary data
- **Time estimation**: Calculates approximate race time based on lap number
- **Duration**: Captures a configurable time window around the incident

### 2. Data Collection

- **Position data**: X/Y coordinates from FastF1 telemetry
- **Track layout**: Realistic track surface from track data files
- **Car images**: Driver-specific car images with proper rotation

### 3. Visualization

- **Follow camera**: Keeps both cars in view during the incident
- **Realistic scaling**: Cars sized according to actual F1 dimensions
- **Smooth animation**: High-quality GIF output with configurable duration

## 📊 Matching with Commentary

### From Commentary Data

The system automatically extracts:
- **Lap numbers** from incident data
- **Driver codes** from messages and driver lists
- **Incident types** (collision, incident, etc.)

### Time Estimation

For precise timing, the system:
1. **Estimates race time** based on lap number and average lap duration
2. **Allows manual override** with `--start_time` parameter
3. **Captures duration** around the estimated incident time

## 🎯 Perfect for Commentary

### Use Cases

- **Collision analysis**: Show exactly what happened during crashes
- **Overtaking moves**: Visualize key passing maneuvers
- **Track limits violations**: See drivers going off track
- **Position changes**: Watch dramatic position swaps

### Integration with Commentary

1. **Generate commentary** with enhanced telemetry data
2. **Extract incident info** from commentary JSON
3. **Create visualizations** for key moments
4. **Match timing** with commentary descriptions

## 🔍 Example: VER vs HAM Collision

From the commentary:
> "AND HERE WE GO, FOLKS! WE'VE GOT A HUGE INCIDENT FOLKS, TURN 1, AND IT'S INVOLVING THE TWO HEAVYWEIGHTS, VERSTAPPEN IN CAR 1 AND HAMILTON IN CAR 44!"

Command to visualize:
```bash
python race_incident_follow.py \
  --year 2024 \
  --race "Hungary" \
  --driver1 "VER" \
  --driver2 "HAM" \
  --lap 63 \
  --start_time "13:45:30" \
  --duration 30 \
  --follow \
  --road
```

## 🛠️ Troubleshooting

### Common Issues

1. **No data found**: Check year, race name, and driver codes
2. **Poor timing**: Adjust `--start_time` or `--duration`
3. **Missing car images**: Script will use colored markers as fallback
4. **Slow generation**: First run downloads data, subsequent runs use cache

### Tips

- **Use follow mode** for close-up incident analysis
- **Add road surface** for better context
- **Adjust duration** based on incident complexity
- **Check cache directory** for downloaded data

## 📈 Advanced Usage

### Custom Timing

For precise timing, you can:
1. **Analyze telemetry data** to find exact incident times
2. **Use manual start_time** instead of estimation
3. **Adjust duration** to capture the full incident

### Batch Processing

Generate multiple incident visualizations:
```bash
# Generate all incidents from commentary
python generate_incident_visualizations.py \
  --commentary crofty_commentary_v3.json \
  --race "Hungary" \
  --year 2024 \
  --max-incidents 10
```

### Integration with Analysis

Combine with race analysis:
1. **Run race analyzer** to identify key moments
2. **Generate commentary** with technical details
3. **Create visualizations** for incidents
4. **Match timing** for perfect synchronization

## 🎉 Result

You'll have animated GIFs that show exactly what happened during the incidents described in your commentary, with:
- **Realistic track layouts**
- **Proper car positioning and rotation**
- **Follow camera for dramatic effect**
- **Perfect timing with commentary**

This creates a complete multimedia experience combining technical commentary with visual proof of what actually happened on track!




