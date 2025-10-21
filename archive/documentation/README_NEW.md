# F1 Commentary

A comprehensive Python toolkit for Formula 1 race data collection, analysis, commentary generation, and visualization. Transform raw F1 telemetry data into engaging commentary and stunning visualizations.

## 🚀 Features

### Data Collection
- **Complete Race Data**: Comprehensive F1 race data collection using FastF1 API
- **Multiple Formats**: Export to JSON, CSV, Excel, or all formats
- **Intelligent Caching**: Built-in caching for faster repeated requests
- **Session Support**: All session types (Practice, Qualifying, Race, Sprint)

### Race Analysis
- **Automatic Incident Detection**: Find collisions, track limits violations, and race control messages
- **Position Change Analysis**: Identify major position changes and overtakes
- **Strategy Analysis**: Analyze pit stop strategies and tire compounds
- **Weather Impact**: Correlate weather conditions with race events
- **Telemetry Analysis**: Deep dive into car telemetry data

### AI Commentary Generation
- **Groq API Integration**: Generate engaging commentary using state-of-the-art language models
- **Multiple Commentary Types**: Incidents, position changes, track limits, collisions
- **David Crofty Style**: Dramatic, live commentary in the style of F1's legendary commentator
- **Technical Accuracy**: Commentary backed by real telemetry data

### Visualization
- **Incident Animations**: Create animated GIFs of specific race incidents
- **Follow Camera**: Dynamic camera that follows cars during incidents
- **Realistic Track Layouts**: Accurate track representations with proper scaling
- **Car Images**: Driver-specific car images with realistic rotation

## 📦 Installation

### From Source
```bash
git clone https://github.com/your-username/f1-commentary.git
cd f1-commentary
pip install -e .
```

### Development Installation
```bash
pip install -e ".[dev]"
```

## 🛠️ Quick Start

### 1. Set up API Keys
```bash
export GROQ_API_KEY="your_groq_api_key_here"
```

### 2. Check System Status
```bash
f1-commentary status
```

### 3. Run Full Pipeline
```bash
# Collect data, analyze, generate commentary, and create visualizations
f1-commentary pipeline --year 2024 --race "Hungary" --session R
```

### 4. Individual Commands
```bash
# Collect race data
f1-commentary collect --year 2024 --race "Hungary" --session R --summary

# Analyze race data
f1-commentary analyze --data-dir ./f1_data_output --race "Hungary" --summary

# Generate commentary
f1-commentary comment --data-file analysis_results/race_analysis_20240101_120000.json

# Create incident visualization
f1-commentary visualize --year 2024 --race "Hungary" --driver1 VER --driver2 HAM --lap 63 --start-time "13:45:30" --duration 30 --follow --road
```

## 📚 Usage Examples

### Python API
```python
from f1_commentary import F1DataCollector, F1RaceAnalyzer, F1CommentaryGenerator

# Collect data
collector = F1DataCollector()
collector.load_session(2024, "Hungary", "R")
data = collector.get_comprehensive_data()
collector.save_data()

# Analyze race
analyzer = F1RaceAnalyzer("./f1_data_output")
analyzer.load_race_data("Hungary")
results = analyzer.generate_comprehensive_analysis()

# Generate commentary
generator = F1CommentaryGenerator(api_key="your_key")
commentaries = generator.process_race_data(results)
```

### Command Line Interface
```bash
# Full pipeline with custom output directory
f1-commentary pipeline --year 2024 --race "Monaco" --output-dir ./monaco_analysis

# Skip certain steps
f1-commentary pipeline --year 2024 --race "Monaco" --skip-visualize

# Verbose logging
f1-commentary collect --year 2024 --race "Monaco" --verbose
```

## 🏗️ Architecture

The package is organized into distinct modules:

```
src/f1_commentary/
├── __init__.py          # Main package interface
├── cli.py              # Command-line interface
├── config/             # Configuration management
│   ├── settings.py     # Application settings
│   └── api_keys.py     # API key management
├── data/               # Data collection
│   ├── collector.py    # F1 data collector
│   └── processor.py    # Data processing utilities
├── analysis/           # Race analysis
│   ├── analyzer.py     # Main race analyzer
│   ├── incident_detector.py
│   └── telemetry_analyzer.py
├── commentary/         # Commentary generation
│   ├── generator.py    # AI commentary generator
│   └── models.py       # Data models
├── visualization/      # Visualization tools
│   ├── incident_visualizer.py
│   └── track_renderer.py
└── utils/              # Utilities
    ├── logging.py      # Logging configuration
    ├── file_utils.py   # File operations
    └── data_utils.py   # Data processing
```

## ⚙️ Configuration

### Environment Variables
```bash
# Required
GROQ_API_KEY=your_groq_api_key

# Optional
F1_CACHE_DIR=./f1_cache
F1_OUTPUT_DIR=./f1_data_output
F1_LOG_LEVEL=INFO
```

### Settings File
Create a `.env` file in your project root:
```env
GROQ_API_KEY=your_groq_api_key_here
F1_CACHE_DIR=./f1_cache
F1_OUTPUT_DIR=./f1_data_output
F1_LOG_LEVEL=INFO
```

## 📊 Output Examples

### Race Analysis
```json
{
  "race_overview": {
    "total_laps": 70,
    "winner": {
      "driver": "VER",
      "name": "Max Verstappen",
      "team": "Red Bull Racing"
    }
  },
  "incidents": [
    {
      "lap": 63,
      "message": "COLLISION BETWEEN CAR 1 AND CAR 44",
      "steward_action": "Under investigation"
    }
  ],
  "commentary_segments": [
    {
      "priority": 1,
      "type": "collision",
      "title": "Collision - Lap 63"
    }
  ]
}
```

### Generated Commentary
```json
{
  "commentaries": [
    {
      "type": "incident",
      "commentary": "AND HERE WE GO, FOLKS! WE'VE GOT A HUGE INCIDENT FOLKS, TURN 1, AND IT'S INVOLVING THE TWO HEAVYWEIGHTS, VERSTAPPEN IN CAR 1 AND HAMILTON IN CAR 44!"
    }
  ]
}
```

## 🎯 Use Cases

### For F1 Fans
- **Race Analysis**: Deep dive into race incidents and strategies
- **Commentary**: Generate engaging commentary for race highlights
- **Visualizations**: Create animated GIFs of key moments

### For Content Creators
- **YouTube Videos**: Generate commentary for race analysis videos
- **Social Media**: Create engaging visualizations for posts
- **Blogs**: Technical analysis with real telemetry data

### For Developers
- **Data Analysis**: Access comprehensive F1 race data
- **Machine Learning**: Use telemetry data for ML projects
- **Visualization**: Create custom race visualizations

## 🔧 Advanced Usage

### Custom Commentary Styles
```python
from f1_commentary.commentary import F1CommentaryGenerator

# Custom system prompt for different commentary styles
generator = F1CommentaryGenerator(api_key="your_key")
generator.system_prompt = "You are a technical F1 analyst..."
```

### Batch Processing
```python
# Process multiple races
races = ["Hungary", "Monaco", "Silverstone"]
for race in races:
    analyzer = F1RaceAnalyzer("./data")
    analyzer.load_race_data(race)
    results = analyzer.generate_comprehensive_analysis()
```

### Custom Visualizations
```python
from f1_commentary.visualization import F1IncidentVisualizer

visualizer = F1IncidentVisualizer()
visualizer.create_custom_animation(
    data1, data2, 
    custom_styling={"car_size": 40, "follow_window": 300}
)
```

## 🧪 Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=f1_commentary

# Run specific test file
pytest tests/test_data_collector.py
```

## 📈 Performance

- **Data Collection**: ~2-5 minutes for full race data (first time)
- **Analysis**: ~30-60 seconds for comprehensive analysis
- **Commentary Generation**: ~1-2 seconds per commentary piece
- **Visualization**: ~10-30 seconds per incident animation

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Setup
```bash
git clone https://github.com/your-username/f1-commentary.git
cd f1-commentary
pip install -e ".[dev]"
pre-commit install
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [FastF1](https://github.com/theOehrly/Fast-F1) for providing the F1 data API
- [Groq](https://groq.com/) for the AI commentary generation
- Formula 1 for the amazing sport and data

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/your-username/f1-commentary/issues)
- **Discussions**: [GitHub Discussions](https://github.com/your-username/f1-commentary/discussions)
- **Documentation**: [Read the Docs](https://f1-commentary.readthedocs.io/)

## 🗺️ Roadmap

- [ ] Real-time race analysis
- [ ] Multi-language commentary support
- [ ] Voice synthesis integration
- [ ] Web dashboard
- [ ] Mobile app
- [ ] Historical race database
- [ ] Machine learning predictions
- [ ] Social media integration

---

**Made with ❤️ for F1 fans and data enthusiasts**
