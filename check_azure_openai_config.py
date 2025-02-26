import requests
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def check_azure_openai_config():
    """
    Check Azure OpenAI configuration by trying different endpoint formats
    and API versions to diagnose the issue.
    """
    # API key from your code
    api_key = "6c0b26151fc04cadae38b20ad67ab241"
    
    # Try different endpoint formats
    endpoints = [
        "https://vals-prod-openai.openai.azure.com",
        "https://vals-prod-openai.azure.openai.com",  # Alternative format
        "https://vals-prod-openai.openai.azure.com/openai",
        "https://vals-prod-openai.openai.azure.com/openai/deployments"
    ]
    
    # Try different API versions
    api_versions = [
        "2024-11-20",
        "2024-02-15",
        "2023-12-01",
        "2023-05-15"
    ]
    
    print("Checking Azure OpenAI configuration...")
    
    # Test basic connectivity to each endpoint
    for endpoint in endpoints:
        print(f"\nTesting endpoint: {endpoint}")
        try:
            headers = {
                "api-key": api_key,
                "Content-Type": "application/json"
            }
            response = requests.get(endpoint, headers=headers)
            print(f"Status code: {response.status_code}")
            print(f"Response: {response.text[:200]}...")  # Show first 200 chars
        except Exception as e:
            print(f"Error: {str(e)}")
    
    # Try to get a list of deployments using different API versions
    base_endpoint = "https://vals-prod-openai.openai.azure.com"
    print("\nTrying to list deployments with different API versions...")
    
    for api_version in api_versions:
        print(f"\nTesting API version: {api_version}")
        try:
            url = f"{base_endpoint}/openai/deployments?api-version={api_version}"
            headers = {
                "api-key": api_key,
                "Content-Type": "application/json"
            }
            response = requests.get(url, headers=headers)
            print(f"Status code: {response.status_code}")
            print(f"Response: {response.text[:200]}...")  # Show first 200 chars
        except Exception as e:
            print(f"Error: {str(e)}")

if __name__ == "__main__":
    check_azure_openai_config() 