# F1 Commentary

Transform F1 race data into engaging commentary and visualizations using AI.

## Quick Start

```bash
# Install
python install.py

# Set API key
export GROQ_API_KEY="your_groq_api_key"

# Run full pipeline
f1-commentary pipeline --year 2024 --race "Hungary" --session R
```

## Commands

```bash
# Collect race data
f1-commentary collect --year 2024 --race "Hungary" --session R

# Analyze race
f1-commentary analyze --data-dir ./f1_data_output --race "Hungary"

# Generate commentary
f1-commentary comment --data-file analysis_results/race_analysis.json

# Create incident visualization
f1-commentary visualize --year 2024 --race "Hungary" --driver1 VER --driver2 HAM --lap 63 --start-time "13:45:30" --duration 30

# Check system status
f1-commentary status
```

## Features

- **Data Collection**: Complete F1 race data via FastF1 API
- **Race Analysis**: Automatic incident detection and position change analysis
- **AI Commentary**: Generate engaging commentary using Groq API
- **Visualizations**: Animated GIFs of race incidents with follow camera

## Requirements

- Python 3.8+
- Groq API key (get from [console.groq.com](https://console.groq.com/keys))

## Installation

```bash
git clone <repository-url>
cd f1-commentary
python install.py
```

## Example

```python
from f1_commentary import F1DataCollector, F1RaceAnalyzer, F1CommentaryGenerator

# Collect data
collector = F1DataCollector()
collector.load_session(2024, "Hungary", "R")
data = collector.get_comprehensive_data()

# Analyze race
analyzer = F1RaceAnalyzer("./f1_data_output")
analyzer.load_race_data("Hungary")
results = analyzer.generate_comprehensive_analysis()

# Generate commentary
generator = F1CommentaryGenerator(api_key="your_key")
commentaries = generator.process_race_data(results)
```

## Documentation

- [Full Documentation](README_NEW.md)
- [Refactoring Summary](REFACTORING_SUMMARY.md)
- [Examples](examples/)

## License

MIT License