#!/usr/bin/env python3
"""
The Language Tribe - Quick Start Script
Description: Simple script to run the language matching algorithm demo
Author: Afreen
Date: 07/01/2025
"""

import sys
import os

# Add current directory to Python path to import our modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def main():
    """Run the language matching algorithm demo"""
    try:
        from demo import main as demo_main
        print("Starting The Language Tribe matching algorithm demo...")
        print()
        demo_main()
    except ImportError as e:
        print(f"Error importing demo module: {e}")
        print("Make sure all required files are in the same directory.")
    except Exception as e:
        print(f"Error running demo: {e}")

if __name__ == "__main__":
    main()