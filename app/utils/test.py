##test_apis.py
"""
API Connection Testing Module

This file provides utilities for verifying connections to all external APIs used in
the radio commercial generation pipeline. It's designed to quickly diagnose
connectivity issues before attempting to generate commercials.

The tests verify three critical API dependencies:
1. Perplexity AI - Used for business research and analysis
2. ElevenLabs - Used for text-to-speech voice generation
3. Azure OpenAI - Alternative AI provider (if configured)

This module is typically run during setup or troubleshooting to ensure
all required services are accessible before proceeding with production.
"""

import os
import sys
import requests
import json

# Add parent directory to path to import config
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.config import Config

def test_azure_openai_api():
    """
    Test Azure OpenAI API connection using deployment name from config.

    Verifies that:
    1. All required Azure configuration values are present
    2. Connection can be established
    3. Simple query returns successful response
    """
    print("Testing Azure OpenAI API...")

    # Check if all required Azure config values are present
    required_azure_configs = [
        Config.AZURE_API_BASE,
        Config.AZURE_API_KEY,
        Config.AZURE_API_VERSION,
        Config.AZURE_DEPLOYMENT_NAME
    ]

    if not all(required_azure_configs):
        print("❌ One or more Azure OpenAI configuration values are missing")
        return False

    headers = {
        "api-key": Config.AZURE_API_KEY,
        "Content-Type": "application/json"
    }

    data = {
        "messages": [
            {"role": "user", "content": "Hello, is this API working?"}
        ],
        "max_tokens": 50
    }

    try:
        endpoint = f"{Config.AZURE_API_BASE}/openai/deployments/{Config.AZURE_DEPLOYMENT_NAME}/chat/completions?api-version={Config.AZURE_API_VERSION}"
        response = requests.post(
            endpoint,
            headers=headers,
            data=json.dumps(data)
        )

        if response.status_code == 200:
            print(f"✅ Azure OpenAI API connection successful (using {Config.AZURE_DEPLOYMENT_NAME})")
            return True
        else:
            print(f"❌ Azure OpenAI API error: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ Azure OpenAI API connection failed: {str(e)}")
        return False


def run_all_tests():
    """
    Run all API tests and report results.

    Executes all individual API tests, collects results,
    and provides a summary of successful connections.

    Returns:
        bool: True if all tests passed, False if any failed
    """
    print("Running API connection tests...\n")

    results = {
        "Azure OpenAI": test_azure_openai_api()
    }

    print("\nSummary:")
    for api_name, result in results.items():
        status = "✅ CONNECTED" if result else "❌ FAILED"
        print(f"{api_name}: {status}")

    # Calculate overall success
    success_count = sum(1 for result in results.values() if result)
    total_count = len(results)

    print(f"\n{success_count}/{total_count} APIs connected successfully")

    return all(results.values())


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)