"""
Local testing script for LeetCode sync
This loads environment variables from a .env file for testing
"""
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Import and run the main script
from daily_sync import main

if __name__ == "__main__":
    print("Starting local test...")
    print(f"TARGET_REPO: {os.getenv('TARGET_REPO')}")
    print(f"LEETCODE_SESSION: {'✓ Set' if os.getenv('LEETCODE_SESSION') else '✗ Missing'}")
    print(f"GITHUB_TOKEN: {'✓ Set' if os.getenv('GITHUB_TOKEN') else '✗ Missing'}")
    print(f"GEMINI_API_KEY: {'✓ Set' if os.getenv('GEMINI_API_KEY') else '✗ Missing'}")
    print("\n" + "="*50 + "\n")
    
    main()
