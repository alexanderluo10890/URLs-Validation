##config.py
"""
Configuration Module

This file centralizes access to API keys and configuration settings used throughout
the radio commercial generation system. It loads sensitive credentials from environment
variables and provides standardized access to these settings.

To use this configuration:
1. Create a .env file in the project root with your API keys
2. Access settings via Config.SETTING_NAME throughout the application

Environment variables required for full functionality:
- PERPLEXITY_API_KEY: For business research and analysis
- ELEVEN_LABS_API_KEY: For text-to-speech conversion
- AZURE_API_BASE: (Optional) For Azure OpenAI integration
- AZURE_API_KEY: (Optional) For Azure OpenAI integration
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Config:
    """
    Configuration class to load environment variables.

    This class provides centralized access to API keys and settings
    used throughout the application. Using a class approach allows
    for easy imports and consistent access patterns across modules.
    """
    # API Keys (loaded from environment variables)
    # Azure OpenAI Settings (alternative AI provider)
    AZURE_API_BASE = os.getenv("AZURE_API_BASE")
    AZURE_API_KEY = os.getenv("AZURE_API_KEY")
    AZURE_API_VERSION = "2024-08-01-preview"  # Hardcoded instead of from env
    AZURE_DEPLOYMENT_NAME = "gpt-4o"  # Hardcoded instead of from env
