#!/usr/bin/env python3
"""Debug script to test raw Gemini API responses"""

import os
import json
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables
ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

try:
    from google import genai

    # Initialize Gemini client
    client = genai.Client(api_key=os.environ['GEMINI_API_KEY'])

    # Test the exact prompt used in the debate endpoint
    topic = "Should artificial intelligence be regulated by governments?"
    prompt = f"""
    Generate balanced debate arguments for the topic: "{topic}"

    Please provide:
    1. 3-4 strong arguments FOR the topic with supporting facts
    2. 3-4 strong arguments AGAINST the topic with supporting facts

    Format the response as JSON with this structure:
    {{
        "arguments_for": [
            {{
                "point": "Main argument point",
                "supporting_facts": ["Fact 1", "Fact 2", "Fact 3"]
            }}
        ],
        "arguments_against": [
            {{
                "point": "Main argument point",
                "supporting_facts": ["Fact 1", "Fact 2", "Fact 3"]
            }}
        ]
    }}

    Ensure arguments are well-researched, factual, and present both sides fairly.
    """

    print("=== Testing Raw Gemini Response ===")
    print(f"Topic: {topic}")
    print("\n--- Sending request to Gemini API ---")

    response = client.models.generate_content(
        model='gemini-2.0-flash-001',
        contents=prompt,
        config={
            'system_instruction': 'You are a knowledgeable debate coach who provides balanced, well-researched arguments for any topic. Always respond with valid JSON only.',
            'temperature': 0.7,
            'max_output_tokens': 2000
        }
    )

    print(f"\n--- Raw Gemini Response ---")
    print(f"Response text: {response.text}")
    print(f"Response length: {len(response.text)}")

    print(f"\n--- Attempting JSON Parse ---")
    try:
        parsed = json.loads(response.text)
        print("✅ JSON parsing successful!")
        print(f"Arguments FOR: {len(parsed.get('arguments_for', []))}")
        print(f"Arguments AGAINST: {len(parsed.get('arguments_against', []))}")

        if parsed.get('arguments_for'):
            print(f"\nFirst argument FOR: {parsed['arguments_for'][0]['point']}")
        if parsed.get('arguments_against'):
            print(f"First argument AGAINST: {parsed['arguments_against'][0]['point']}")

    except json.JSONDecodeError as e:
        print(f"❌ JSON parsing failed: {e}")
        print("This is why the backend falls back to mock data!")

        # Let's try to extract JSON from the response
        text = response.text.strip()
        if text.startswith('```json'):
            # Remove markdown code blocks
            text = text.replace('```json', '').replace('```', '').strip()
            print(f"\n--- Trying without markdown ---")
            try:
                parsed = json.loads(text)
                print("✅ JSON parsing successful after removing markdown!")
            except json.JSONDecodeError as e2:
                print(f"❌ Still failed: {e2}")

except ImportError:
    print("❌ google-genai not installed")
except Exception as e:
    print(f"❌ Error: {e}")