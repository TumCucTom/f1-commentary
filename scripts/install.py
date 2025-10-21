#!/usr/bin/env python3
"""
Installation script for F1 Commentary package.

This script helps users set up the F1 Commentary package with proper
configuration and API keys.
"""

import os
import sys
import subprocess
from pathlib import Path


def run_command(command, description):
    """Run a command and handle errors."""
    print(f"  {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"  ✓ {description} completed")
        return True
    except subprocess.CalledProcessError as e:
        print(f"  ✗ {description} failed: {e}")
        if e.stdout:
            print(f"    stdout: {e.stdout}")
        if e.stderr:
            print(f"    stderr: {e.stderr}")
        return False


def check_python_version():
    """Check if Python version is compatible."""
    print("Checking Python version...")
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print(f"  ✗ Python {version.major}.{version.minor} is not supported")
        print("  Please install Python 3.8 or higher")
        return False
    else:
        print(f"  ✓ Python {version.major}.{version.minor}.{version.micro} is compatible")
        return True


def install_package():
    """Install the F1 Commentary package."""
    print("Installing F1 Commentary package...")
    
    # Check if we're in the right directory
    if not Path("setup.py").exists():
        print("  ✗ setup.py not found. Please run this script from the package root directory.")
        return False
    
    # Install the package
    if not run_command("pip install -e .", "Installing package in development mode"):
        return False
    
    return True


def setup_environment():
    """Set up environment variables and configuration."""
    print("Setting up environment...")
    
    # Create .env file if it doesn't exist
    env_file = Path(".env")
    if not env_file.exists():
        print("  Creating .env file...")
        env_content = """# F1 Commentary Configuration
# Get your Groq API key from: https://console.groq.com/keys
GROQ_API_KEY=your_groq_api_key_here

# Optional: Custom directories
# F1_CACHE_DIR=./f1_cache
# F1_OUTPUT_DIR=./f1_data_output
# F1_LOG_LEVEL=INFO
"""
        env_file.write_text(env_content)
        print("  ✓ Created .env file")
        print("  ⚠️  Please edit .env file and add your Groq API key")
    else:
        print("  ✓ .env file already exists")
    
    # Create directories
    directories = ["f1_cache", "f1_data_output", "analysis_results", "incident_visualizations"]
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        print(f"  ✓ Created directory: {directory}")


def test_installation():
    """Test the installation."""
    print("Testing installation...")
    
    # Test import
    try:
        import f1_commentary
        print("  ✓ Package import successful")
    except ImportError as e:
        print(f"  ✗ Package import failed: {e}")
        return False
    
    # Test CLI
    if not run_command("f1-commentary --help", "Testing CLI interface"):
        return False
    
    # Test status command
    if not run_command("f1-commentary status", "Testing status command"):
        return False
    
    return True


def main():
    """Main installation function."""
    print("F1 Commentary Package Installation")
    print("=" * 40)
    
    # Check Python version
    if not check_python_version():
        return 1
    
    # Install package
    if not install_package():
        print("\nInstallation failed. Please check the error messages above.")
        return 1
    
    # Set up environment
    setup_environment()
    
    # Test installation
    if not test_installation():
        print("\nInstallation test failed. Please check the error messages above.")
        return 1
    
    print("\n" + "=" * 40)
    print("Installation completed successfully! 🎉")
    print("\nNext steps:")
    print("1. Edit the .env file and add your Groq API key")
    print("2. Run 'f1-commentary status' to check your setup")
    print("3. Try the example: 'python examples/basic_usage.py'")
    print("4. Read the documentation: README_NEW.md")
    print("\nQuick start:")
    print("  f1-commentary pipeline --year 2024 --race 'Hungary' --session R")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
