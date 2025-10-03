# F1 Commentary Generator

Transform F1 race data into engaging commentary using the Groq API. This tool takes detailed telemetry analysis and converts it into compelling F1 commentary sentences.

## 🚀 Features

- **Incident Commentary**: Detailed analysis of collisions and incidents
- **Position Change Analysis**: Explains dramatic position drops with telemetry data
- **Track Limits Commentary**: Analyzes violations with speed and sector data
- **Collision Analysis**: Deep dive into collision telemetry
- **Race Summary**: Overall race story and key moments

## 📋 Prerequisites

1. **Groq API Key**: Get one from [Groq Console](https://console.groq.com/keys)
2. **Race Data**: Run the enhanced telemetry analysis first
3. **Python Dependencies**: Install required packages

## 🛠️ Setup

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Set API Key
```bash
export GROQ_API_KEY='your_api_key_here'
```

### 3. Run Setup Check
```bash
python setup_commentary.py
```

### 4. Generate Race Data (if needed)
```bash
python enhanced_telemetry_example.py
```

## 🎯 Usage

### Command Line
```bash
# Generate commentary from race data
python commentary_generator.py --data_file detailed_telemetry_analysis.json

# Specify output file
python commentary_generator.py --data_file detailed_telemetry_analysis.json --output my_commentary.json

# Use different model
python commentary_generator.py --data_file detailed_telemetry_analysis.json --model llama-3.1-8b-instant
```

### Programmatic Usage
```python
from commentary_generator import F1CommentaryGenerator
import json

# Load race data
with open('detailed_telemetry_analysis.json', 'r') as f:
    race_data = json.load(f)

# Initialize generator
generator = F1CommentaryGenerator(api_key="your_api_key")

# Generate specific commentary
incident_commentary = generator.generate_incident_commentary(race_data['incidents'][0])
position_commentary = generator.generate_position_change_commentary(race_data['major_position_changes'][0])

# Generate all commentary
all_commentaries = generator.process_race_data(race_data)
```

### Example Script
```bash
python generate_commentary_example.py
```

## 📊 Commentary Types

### 1. Incident Commentary
Analyzes incidents with telemetry data:
- Position changes around incidents
- Speed analysis and anomalies
- Tire compound and life data
- Steward decisions

**Example Output:**
> "Verstappen's early race incident at Turn 1 saw him maintain consistent speeds around 243-249 km/h on medium tires, but resulted in a position drop from 2nd to 3rd place, showing the fine margins in F1 racing."

### 2. Position Change Commentary
Explains dramatic position changes:
- Lap time comparisons
- Speed changes across sectors
- Tire compound changes
- Sector time breakdowns

**Example Output:**
> "Stroll's dramatic 8-position drop on Lap 15 was caused by a massive 16.7-second lap time increase, primarily due to a 19.3-second slowdown in Sector 1 during his pit stop from soft to medium tires, highlighting the strategic gamble that backfired."

### 3. Track Limits Commentary
Analyzes violations with telemetry:
- Speed analysis around violations
- Turn-specific analysis
- Sector time impact
- Deleted lap times

**Example Output:**
> "Verstappen's track limits violation at Turn 2 on Lap 36 occurred at 250 km/h, with his deleted 1:25.757 lap time showing the aggressive driving style that cost him valuable track position."

### 4. Collision Commentary
Deep analysis of collisions:
- Detailed lap-by-lap telemetry
- Speed and position analysis
- Tire and compound data
- Impact assessment

**Example Output:**
> "The Verstappen-Hamilton collision at Turn 1 on Lap 63 involved both drivers maintaining speeds around 245-250 km/h, with the incident occurring as they battled for podium positions, resulting in a steward investigation that would determine the race outcome."

## 🔧 Configuration

### Available Models
- `llama-3.1-70b-versatile` (default) - Best quality
- `llama-3.1-8b-instant` - Faster, lower cost
- `mixtral-8x7b-32768` - Alternative option

### Customization
Modify the system prompt in `commentary_generator.py` to change the commentary style:
```python
"content": "You are an expert F1 commentator with deep technical knowledge. Write engaging, informative commentary that explains what happened in racing terms that fans can understand. Be specific about speeds, times, and technical details."
```

## 📁 Output Format

The generator creates JSON output with:
```json
{
  "race_info": {
    "data_file": "detailed_telemetry_analysis.json",
    "model_used": "llama-3.1-70b-versatile",
    "total_commentaries": 15
  },
  "commentaries": [
    {
      "incident": {...},
      "commentary": "Generated commentary text...",
      "type": "incident"
    }
  ]
}
```

## 🎯 Example Workflow

1. **Collect Race Data**
   ```bash
   python f1_race_data.py --year 2024 --event "Hungary Grand Prix" --session R
   ```

2. **Analyze Telemetry**
   ```bash
   python enhanced_telemetry_example.py
   ```

3. **Generate Commentary**
   ```bash
   python commentary_generator.py --data_file detailed_telemetry_analysis.json
   ```

4. **Review Results**
   ```bash
   cat commentary_output.json | jq '.commentaries[].commentary'
   ```

## 🚨 Troubleshooting

### Common Issues

1. **API Key Not Set**
   ```
   Error: GROQ_API_KEY environment variable not set
   ```
   Solution: Set your API key with `export GROQ_API_KEY='your_key'`

2. **Missing Data File**
   ```
   Error: detailed_telemetry_analysis.json not found
   ```
   Solution: Run the enhanced telemetry analysis first

3. **API Rate Limits**
   ```
   API call failed: 429 Too Many Requests
   ```
   Solution: The script includes rate limiting, but you may need to wait

4. **Model Not Available**
   ```
   Error: Model not found
   ```
   Solution: Check available models at [Groq Console](https://console.groq.com/docs/models)

### Debug Mode
Add debug prints to see API responses:
```python
print(f"API Response: {result}")
```

## 📈 Performance

- **Processing Time**: ~1-2 seconds per commentary piece
- **Rate Limits**: 1 second delay between API calls
- **Cost**: ~$0.01-0.05 per race analysis (depending on model)
- **Quality**: High-quality, contextually relevant commentary

## 🔮 Future Enhancements

- **Multi-language Support**: Generate commentary in different languages
- **Voice Synthesis**: Convert commentary to audio
- **Real-time Analysis**: Live race commentary generation
- **Custom Styles**: Different commentator personalities
- **Visual Integration**: Combine with race footage

## 📝 License

This tool is provided as-is for educational and research purposes. Please respect the Groq API terms of service and F1 data usage policies.
