#!/usr/bin/env python3
"""
Test script for F1 Race Incident Follow functionality

This script demonstrates the incident follow functionality with a working example.
"""

import subprocess
import os


def test_incident_follow():
    """Test the incident follow functionality with a known working example."""
    
    print("=== Testing F1 Race Incident Follow ===\n")
    
    # Test with a later lap and more realistic time
    # Hungary 2024 race started around 15:00 local time (13:00 UTC)
    # Let's try lap 20 with a more realistic time
    
    print("Testing with Lap 20 (more realistic timing)...")
    
    cmd = [
        'python', 'race_incident_follow.py',
        '--year', '2024',
        '--race', 'Hungary',
        '--driver1', 'VER',
        '--driver2', 'HAM',
        '--lap', '20',
        '--start_time', '13:30:00',  # More realistic time for lap 20
        '--duration', '30',
        '--follow',
        '--road',
        '--gif-seconds', '5'  # Shorter GIF for testing
    ]
    
    try:
        print("Running command:")
        print(' '.join(cmd))
        print()
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        
        if result.returncode == 0:
            print("✅ Successfully created incident visualization!")
            print("Check for the generated GIF file in the current directory.")
            return True
        else:
            print("❌ Failed to create visualization")
            print(f"Error: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print("⏰ Command timed out")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_commentary_extraction():
    """Test the commentary extraction functionality."""
    
    print("\n=== Testing Commentary Extraction ===\n")
    
    cmd = [
        'python', 'generate_incident_visualizations.py',
        '--commentary', 'crofty_commentary_v3.json',
        '--race', 'Hungary',
        '--year', '2024',
        '--max-incidents', '1'
    ]
    
    try:
        print("Running command:")
        print(' '.join(cmd))
        print()
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        
        print("Output:")
        print(result.stdout)
        
        if result.returncode == 0:
            print("✅ Successfully extracted incident information!")
            return True
        else:
            print("❌ Failed to extract incidents")
            print(f"Error: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print("⏰ Command timed out")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def main():
    """Main test function."""
    
    print("F1 Race Incident Follow - Test Suite")
    print("=" * 50)
    
    # Check if required files exist
    if not os.path.exists('crofty_commentary_v3.json'):
        print("❌ crofty_commentary_v3.json not found")
        print("Please run the commentary generator first to create this file.")
        return
    
    if not os.path.exists('race_incident_follow.py'):
        print("❌ race_incident_follow.py not found")
        return
    
    # Run tests
    print("\n1. Testing Commentary Extraction")
    extraction_success = test_commentary_extraction()
    
    print("\n2. Testing Incident Follow (Manual)")
    follow_success = test_incident_follow()
    
    print("\n=== Test Results ===")
    print(f"Commentary Extraction: {'✅ PASS' if extraction_success else '❌ FAIL'}")
    print(f"Incident Follow: {'✅ PASS' if follow_success else '❌ FAIL'}")
    
    if extraction_success and follow_success:
        print("\n🎉 All tests passed! The incident follow system is working correctly.")
    else:
        print("\n⚠️  Some tests failed. Check the output above for details.")


if __name__ == "__main__":
    main()




