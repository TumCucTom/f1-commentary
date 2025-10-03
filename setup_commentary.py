#!/usr/bin/env python3
"""
Setup script for F1 Commentary Generator

This script helps set up the commentary generator by checking dependencies
and providing instructions for API key setup.
"""

import os
import sys
import subprocess


def check_dependencies():
    """Check if required dependencies are installed."""
    print("Checking dependencies...")
    
    required_packages = [
        'requests',
        'pandas',
        'numpy',
        'fastf1'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"✓ {package}")
        except ImportError:
            missing_packages.append(package)
            print(f"✗ {package} (missing)")
    
    if missing_packages:
        print(f"\nMissing packages: {', '.join(missing_packages)}")
        print("Install them with: pip install -r requirements.txt")
        return False
    
    print("✓ All dependencies installed")
    return True


def check_api_key():
    """Check if Groq API key is set."""
    print("\nChecking API key...")
    
    api_key = os.getenv('GROQ_API_KEY')
    if api_key:
        print("✓ GROQ_API_KEY environment variable is set")
        return True
    else:
        print("✗ GROQ_API_KEY environment variable not set")
        print("\nTo set your API key:")
        print("1. Get your API key from: https://console.groq.com/keys")
        print("2. Set the environment variable:")
        print("   export GROQ_API_KEY='your_api_key_here'")
        print("3. Or add it to your .bashrc/.zshrc for persistence")
        return False


def check_data_files():
    """Check if required data files exist."""
    print("\nChecking data files...")
    
    required_files = [
        'detailed_telemetry_analysis.json',
        'race_analyzer.py',
        'commentary_generator.py'
    ]
    
    missing_files = []
    
    for file in required_files:
        if os.path.exists(file):
            print(f"✓ {file}")
        else:
            missing_files.append(file)
            print(f"✗ {file} (missing)")
    
    if missing_files:
        print(f"\nMissing files: {', '.join(missing_files)}")
        if 'detailed_telemetry_analysis.json' in missing_files:
            print("Run the enhanced telemetry analysis first:")
            print("python enhanced_telemetry_example.py")
        return False
    
    print("✓ All required files present")
    return True


def test_api_connection():
    """Test the Groq API connection."""
    print("\nTesting API connection...")
    
    api_key = os.getenv('GROQ_API_KEY')
    if not api_key:
        print("✗ Cannot test API - no API key set")
        return False
    
    try:
        from commentary_generator import F1CommentaryGenerator
        generator = F1CommentaryGenerator(api_key)
        
        # Test with a simple prompt
        test_prompt = "Write one sentence about F1 racing."
        result = generator._call_groq_api(test_prompt)
        
        if result:
            print("✓ API connection successful")
            print(f"Test response: {result[:100]}...")
            return True
        else:
            print("✗ API connection failed")
            return False
            
    except Exception as e:
        print(f"✗ API test failed: {e}")
        return False


def main():
    """Main setup function."""
    print("F1 Commentary Generator Setup")
    print("=" * 40)
    
    # Check all requirements
    deps_ok = check_dependencies()
    api_ok = check_api_key()
    files_ok = check_data_files()
    
    if not deps_ok:
        print("\n❌ Setup incomplete - missing dependencies")
        return
    
    if not files_ok:
        print("\n❌ Setup incomplete - missing data files")
        return
    
    if api_ok:
        # Test API if key is available
        api_test_ok = test_api_connection()
        
        if api_test_ok:
            print("\n✅ Setup complete! Ready to generate commentary.")
            print("\nNext steps:")
            print("1. Run: python generate_commentary_example.py")
            print("2. Or run: python commentary_generator.py --data_file detailed_telemetry_analysis.json")
        else:
            print("\n⚠️  Setup mostly complete, but API test failed.")
            print("Check your API key and try again.")
    else:
        print("\n⚠️  Setup mostly complete, but API key not set.")
        print("Set your GROQ_API_KEY and run this script again.")


if __name__ == "__main__":
    main()
