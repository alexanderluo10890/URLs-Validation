from openai import AzureOpenAI
import argparse
import sys

def test_azure_openai(api_key, api_version, azure_endpoint, deployment_name):
    """
    Test Azure OpenAI connection with the provided configuration.
    
    Args:
        api_key (str): Azure OpenAI API key
        api_version (str): API version (e.g., "2024-11-20")
        azure_endpoint (str): Azure OpenAI endpoint URL
        deployment_name (str): Deployment name to test
    """
    print(f"Testing Azure OpenAI with the following configuration:")
    print(f"API Version: {api_version}")
    print(f"Endpoint: {azure_endpoint}")
    print(f"Deployment Name: {deployment_name}")
    print(f"API Key: {api_key[:5]}...{api_key[-4:]} (partially hidden)")
    
    try:
        # Initialize client
        client = AzureOpenAI(
            api_key=api_key,
            api_version=api_version,
            azure_endpoint=azure_endpoint
        )
        
        # Test with a simple completion
        response = client.chat.completions.create(
            model=deployment_name,
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Hello, this is a test message. Please respond with a short greeting."}
            ],
            max_tokens=50
        )
        
        print("\n✅ Success! Connection to Azure OpenAI is working.")
        print(f"Response: {response.choices[0].message.content}")
        
        # Provide the correct code to use in your application
        print("\nUse the following code in your application:")
        print(f"""
from openai import AzureOpenAI

client = AzureOpenAI(
    api_key="{api_key}",
    api_version="{api_version}",
    azure_endpoint="{azure_endpoint}"
)

response = client.chat.completions.create(
    model="{deployment_name}",  # This is your deployment name
    messages=[
        {{"role": "system", "content": "You are a helpful assistant."}},
        {{"role": "user", "content": "Your prompt here"}}
    ],
    temperature=0,
    max_tokens=800
)
        """)
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        print("\nTroubleshooting tips:")
        print("1. Verify your API key is correct and active")
        print("2. Check that the deployment name exists in your Azure OpenAI resource")
        print("3. Confirm the API version is supported")
        print("4. Ensure your Azure endpoint URL is correct (format: https://<resource-name>.openai.azure.com)")
        print("5. Check if your IP address is allowed in the network settings of your Azure OpenAI resource")

def main():
    parser = argparse.ArgumentParser(description="Test Azure OpenAI connection")
    parser.add_argument("--api-key", required=True, help="Azure OpenAI API key")
    parser.add_argument("--api-version", default="2024-11-20", help="API version (default: 2024-11-20)")
    parser.add_argument("--endpoint", required=True, help="Azure OpenAI endpoint URL")
    parser.add_argument("--deployment", required=True, help="Deployment name to test")
    
    if len(sys.argv) == 1:
        parser.print_help()
        print("\nExample usage:")
        print("python azure_openai_tester.py --api-key YOUR_API_KEY --endpoint https://your-resource.openai.azure.com --deployment gpt-4")
        sys.exit(1)
    
    args = parser.parse_args()
    test_azure_openai(args.api_key, args.api_version, args.endpoint, args.deployment)

if __name__ == "__main__":
    main() 