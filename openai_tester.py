"""
Quick script to verify your OpenAI API key is working.
Usage: python openai_tester.py
"""
import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

def test_openai():
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        print("❌ OPENAI_API_KEY not found in .env file")
        return

    print(f"API Key: {api_key[:8]}...{api_key[-4:]} (partially hidden)")

    client = OpenAI(api_key=api_key)

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": "Say hello in one word."}],
            max_tokens=10
        )
        print(f"✅ OpenAI connection working. Response: {response.choices[0].message.content}")
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    test_openai()
