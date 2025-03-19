"""
This module processes vertical market analysis.
"""

import json
import os
import time
import logging
from openai import AzureOpenAI
from dotenv import load_dotenv
from typing import Dict, Any
from app.prompts.vertical_market_prompts import get_vertical_market_prompt, get_vertical_market_system_message

# -----------------------------------------------------------------------------
# Logging Setup
# -----------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

# -----------------------------------------------------------------------------
# Load environment variables from .env file
# -----------------------------------------------------------------------------
load_dotenv()

# -----------------------------------------------------------------------------
# Initialize Azure OpenAI client with the correct Azure settings
# -----------------------------------------------------------------------------
client = AzureOpenAI(
    api_key="c15e05017b07470f86d6192aa2755d37",
    api_version="2024-12-01-preview",  # Updated API version
    azure_endpoint="https://valstone-prod-openai.openai.azure.com"
)

# -----------------------------------------------------------------------------
# Function: build_report_prompt
# -----------------------------------------------------------------------------
def build_report_prompt(report_text: str) -> str:
    """
    Constructs the prompt for OpenAI based on the generated report.
    
    Args:
        report_text (str): The text content of the final report.
        
    Returns:
        str: The prompt to send to OpenAI.
    """
    prompt = get_vertical_market_prompt(report_text)
    logger.debug("Report prompt constructed.")
    return prompt

# -----------------------------------------------------------------------------
# Function: send_prompt_to_openai
# -----------------------------------------------------------------------------
def send_prompt_to_openai(prompt: str, max_retries: int = 3, retry_delay: int = 5) -> Dict[str, Any]:
    """
    Sends the prompt to Azure OpenAI using the 'o3-mini' deployment and returns the JSON output.
    
    Args:
        prompt (str): The prompt to send to OpenAI.
        max_retries (int): Maximum number of retry attempts.
        retry_delay (int): Delay in seconds between retries.
        
    Returns:
        Dict[str, Any]: The structured JSON output from OpenAI.
        
    Raises:
        RuntimeError: If all retry attempts fail.
    """
    attempt = 0
    last_error = None
    
    system_message = get_vertical_market_system_message()
    
    while attempt < max_retries:
        try:
            logger.info(f"Sending request to OpenAI (attempt {attempt + 1}/{max_retries})...")
            response = client.chat.completions.create(
                model="o3-mini",  # using the o3-mini deployment
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"}
            )
            
            raw_output = response.choices[0].message.content
            
            if not raw_output or not raw_output.strip():
                raise ValueError("OpenAI returned an empty response")
            
            try:
                data_dict: Dict[str, Any] = json.loads(raw_output)
                logger.info("Successfully received and parsed JSON response from OpenAI.")
                return data_dict
            except json.JSONDecodeError as e:
                logger.error(f"JSON parsing error: {str(e)}")
                logger.debug(f"Response snippet: {raw_output[:100]}...")
                raise ValueError(f"Failed to parse JSON response: {str(e)}")
        except Exception as e:
            last_error = e
            attempt += 1
            logger.error(f"Attempt {attempt}/{max_retries} failed: {str(e)}")
            if attempt < max_retries:
                logger.info(f"Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
    
    raise RuntimeError(f"Azure OpenAI API Error after {max_retries} attempts: {str(last_error)}")

# -----------------------------------------------------------------------------
# Function: load_report
# -----------------------------------------------------------------------------
def load_report(filename: str) -> str:
    """
    Load a report from a JSON file.
    
    Args:
        filename (str): The name of the file to load
        
    Returns:
        str: The report content as a string
        
    Raises:
        FileNotFoundError: If the file doesn't exist
        ValueError: If the file is empty or invalid JSON
    """
    if not os.path.exists(filename):
        raise FileNotFoundError(f"Report file not found: {filename}")
    
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            report_data = json.load(f)
            return json.dumps(report_data, indent=2)
    except json.JSONDecodeError:
        raise ValueError(f"Invalid JSON in file: {filename}")
    except Exception as e:
        raise ValueError(f"Error loading report: {str(e)}")

# -----------------------------------------------------------------------------
# Function: save_response
# -----------------------------------------------------------------------------
def save_response(response_data: dict, filename: str) -> None:
    """
    Save a response to a JSON file.
    
    Args:
        response_data (dict): The response data to save
        filename (str): The name of the file to save to
    """
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(response_data, f, indent=2, ensure_ascii=False)
        logger.info(f"Response saved to {filename}")
    except Exception as e:
        logger.error(f"Error saving response to JSON: {e}")
        raise