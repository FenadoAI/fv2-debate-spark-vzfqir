#!/usr/bin/env python3
"""Test script for Gemini API integration"""

import requests
import json
import sys


def test_gemini_endpoint():
    """Test the new Gemini endpoint"""
    base_url = "http://localhost:8001/api"

    # Test data
    test_data = {
        "prompt": "Write a short poem about artificial intelligence",
        "max_tokens": 200,
        "temperature": 0.7
    }

    print("Testing Gemini API endpoint...")
    print(f"Request: {json.dumps(test_data, indent=2)}")

    try:
        response = requests.post(
            f"{base_url}/gemini-generate",
            json=test_data,
            timeout=30
        )

        print(f"Status Code: {response.status_code}")

        if response.status_code == 200:
            result = response.json()
            print("✅ Success!")
            print(f"Model: {result['model']}")
            print(f"Response: {result['response']}")
        else:
            print("❌ Error:")
            print(response.text)

    except Exception as e:
        print(f"❌ Request failed: {str(e)}")


def test_debate_endpoint():
    """Test the updated debate endpoint (now using Gemini)"""
    base_url = "http://localhost:8001/api"

    test_data = {
        "topic": "Should artificial intelligence be regulated by governments?"
    }

    print("\nTesting debate endpoint (now with Gemini)...")
    print(f"Request: {json.dumps(test_data, indent=2)}")

    try:
        response = requests.post(
            f"{base_url}/generate-debate",
            json=test_data,
            timeout=30
        )

        print(f"Status Code: {response.status_code}")

        if response.status_code == 200:
            result = response.json()
            print("✅ Success!")
            print(f"Topic: {result['topic']}")
            print(f"Arguments FOR: {len(result['arguments_for'])} arguments")
            print(f"Arguments AGAINST: {len(result['arguments_against'])} arguments")

            # Show first argument from each side
            if result['arguments_for']:
                print(f"\nFirst argument FOR: {result['arguments_for'][0]['point']}")
            if result['arguments_against']:
                print(f"First argument AGAINST: {result['arguments_against'][0]['point']}")
        else:
            print("❌ Error:")
            print(response.text)

    except Exception as e:
        print(f"❌ Request failed: {str(e)}")


def test_health_check():
    """Test basic health check"""
    base_url = "http://localhost:8001/api"

    try:
        response = requests.get(f"{base_url}/", timeout=10)
        if response.status_code == 200:
            print("✅ Server is running")
            return True
        else:
            print(f"❌ Server responded with status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Server not reachable: {str(e)}")
        return False


if __name__ == "__main__":
    print("=== Testing Gemini API Integration ===\n")

    # Test server health first
    if not test_health_check():
        print("❌ Server is not running. Please start it first.")
        sys.exit(1)

    # Test Gemini endpoint
    test_gemini_endpoint()

    # Test updated debate endpoint
    test_debate_endpoint()

    print("\n=== Tests completed ===")