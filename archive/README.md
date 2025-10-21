# Archive Directory

This directory contains legacy files from the original F1 commentary codebase that have been refactored into the new package structure.

## Directory Structure

### `legacy_scripts/`
Original standalone Python scripts that have been refactored into the new package:
- `f1_race_data.py` → `src/f1_commentary/data/collector.py`
- `race_analyzer.py` → `src/f1_commentary/analysis/analyzer.py`
- `commentary_generator.py` → `src/f1_commentary/commentary/generator.py`
- `race_incident_follow.py` → `src/f1_commentary/visualization/incident_visualizer.py`
- `crofty_commentary_generator.py` → Legacy version of commentary generator

### `examples/`
Original example scripts and test files:
- `analyze_race_example.py` → Use `examples/basic_usage.py` instead
- `enhanced_telemetry_example.py` → Integrated into main package
- `example_incident_follow.py` → Use CLI `f1-commentary visualize` instead
- `example_usage.py` → Use `examples/basic_usage.py` instead
- `generate_commentary_example.py` → Use CLI `f1-commentary comment` instead
- `generate_incident_visualizations.py` → Use CLI `f1-commentary visualize` instead
- `setup_commentary.py` → Use `scripts/install.py` instead
- `test_groq_api.py` → Use `f1-commentary status` instead
- `test_incident_follow.py` → Use CLI `f1-commentary visualize` instead

### `outputs/`
Generated output files from previous runs:
- Analysis data and results
- Generated commentary files
- Visualization images and GIFs
- Log files and summaries

### `documentation/`
Original documentation files that have been consolidated:
- `COMMENTARY_GENERATOR_README.md` → See main `README.md`
- `ENHANCED_ANALYSIS_SUMMARY.md` → See main `README.md`
- `FINAL_SUMMARY.md` → See `REFACTORING_SUMMARY.md`
- `INCIDENT_FOLLOW_README.md` → See main `README.md`
- `incident_summary.md` → See main `README.md`
- `README_NEW.md` → Comprehensive documentation (kept for reference)
- `REFACTORING_SUMMARY.md` → Detailed refactoring information

## Migration Guide

All functionality from these legacy files has been preserved in the new package structure:

1. **Use the CLI**: `f1-commentary` command with subcommands
2. **Use the Python API**: Import from `f1_commentary` package
3. **See examples**: Check `examples/basic_usage.py`
4. **Read documentation**: See main `README.md`

## Note

These files are kept for reference and historical purposes. The new package structure provides all the same functionality with improved organization, testing, and documentation.
