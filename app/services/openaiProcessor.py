"""
This module handles the interaction with Azure OpenAI API for generating business reports.
"""

import json
import logging
import time
from typing import Dict, Any
from pydantic import ValidationError
from app.models.reportsModels import HighLevelBusinessWebsiteScrapeReport
from app.prompts.report_prompts import get_system_message
from dotenv import load_dotenv
from openai import AzureOpenAI

# -----------------------------------------------------------------------------
# Logging Setup
# -----------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

# Load environment variables from .env file
load_dotenv()

# Initialize Azure OpenAI client with the correct Azure settings
client = AzureOpenAI(
    api_key="c15e05017b07470f86d6192aa2755d37",
    api_version="2024-08-01-preview",
    azure_endpoint="https://valstone-prod-openai.openai.azure.com"
)

def send_prompt_to_openai(prompt: str, max_retries: int = 3, retry_delay: int = 5) -> Dict[str, Any]:
    """
    Sends the prompt to Azure OpenAI and returns the structured JSON output.
    
    Args:
        prompt (str): The prompt to send to OpenAI
        max_retries (int, optional): Maximum number of retry attempts. Defaults to 3.
        retry_delay (int, optional): Delay between retries in seconds. Defaults to 5.
    
    Returns:
        Dict[str, Any]: The structured JSON output from OpenAI
        
    Raises:
        RuntimeError: If all retry attempts fail
    """
    attempt = 0
    last_error = None
    
    while attempt < max_retries:
        try:
            logger.info(f"Sending request to OpenAI (attempt {attempt + 1}/{max_retries})...")
            
            response = client.chat.completions.create(
                model="gpt-4o",  # Use the correct deployment name
                messages=[
                    {"role": "system", "content": get_system_message()},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"},
                temperature=0,
            )
            
            raw_json_output = response.choices[0].message.content
            
            # Validate that we got a non-empty response
            if not raw_json_output or not raw_json_output.strip():
                raise ValueError("OpenAI returned an empty response")
            
            # Parse the JSON response
            try:
                data_dict: Dict[str, Any] = json.loads(raw_json_output)
                logger.info("Successfully received and parsed JSON response from OpenAI")
                
                # Log the structure of the received JSON for debugging
                logger.info("JSON structure received:")
                for key in data_dict:
                    logger.info(f"- {key}")
                    if isinstance(data_dict[key], dict):
                        for subkey in data_dict[key]:
                            logger.info(f"  - {subkey}")
                
                return data_dict
            except json.JSONDecodeError as e:
                logger.error(f"JSON parsing error: {str(e)}")
                logger.error(f"First 100 chars of response: {raw_json_output[:100]}...")
                raise ValueError(f"Failed to parse JSON response: {str(e)}")
            
        except Exception as e:
            last_error = e
            attempt += 1
            logger.error(f"Attempt {attempt}/{max_retries} failed: {str(e)}")
            
            if attempt < max_retries:
                logger.info(f"Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
    
    # If we've exhausted all retries, raise the last error
    raise RuntimeError(f"Azure OpenAI API Error after {max_retries} attempts: {str(last_error)}")

def parse_into_pydantic(data_dict: Dict[str, Any]) -> HighLevelBusinessWebsiteScrapeReport:
    """
    Parses the dictionary into a HighLevelBusinessWebsiteScrapeReport model.
    
    Args:
        data_dict (Dict[str, Any]): The dictionary to parse
        
    Returns:
        HighLevelBusinessWebsiteScrapeReport: The parsed Pydantic model
        
    Raises:
        ValueError: If the dictionary doesn't match the Pydantic model
    """
    try:
        report_model = HighLevelBusinessWebsiteScrapeReport(**data_dict)
        return report_model
    except ValidationError as e:
        raise ValueError(f"JSON does not match the Pydantic model: {e}")
