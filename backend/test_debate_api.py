#!/usr/bin/env python3

import requests
import json

# Test the debate generation API
def test_debate_api():
    api_base_url = "https://8001-irinajr69yng4kycuc4o4.e2b.app"
    endpoint = f"{api_base_url}/api/generate-debate"

    # Test data
    test_topic = "Should social media be regulated by government"

    # Make the API call
    try:
        response = requests.post(
            endpoint,
            json={"topic": test_topic},
            headers={"Content-Type": "application/json"},
            timeout=30
        )

        print(f"Status Code: {response.status_code}")
        print(f"Response Headers: {response.headers}")

        if response.status_code == 200:
            data = response.json()
            print("\n=== DEBATE ARGUMENTS ===")
            print(f"Topic: {data['topic']}")

            print("\n--- ARGUMENTS FOR ---")
            for i, arg in enumerate(data['arguments_for'], 1):
                print(f"{i}. {arg['point']}")
                for fact in arg['supporting_facts']:
                    print(f"   • {fact}")
                print()

            print("--- ARGUMENTS AGAINST ---")
            for i, arg in enumerate(data['arguments_against'], 1):
                print(f"{i}. {arg['point']}")
                for fact in arg['supporting_facts']:
                    print(f"   • {fact}")
                print()
        else:
            print(f"Error: {response.text}")

    except Exception as e:
        print(f"Error calling API: {str(e)}")

if __name__ == "__main__":
    test_debate_api()