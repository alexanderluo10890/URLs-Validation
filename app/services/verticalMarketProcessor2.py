import json
import os
import time
import argparse
import logging
from openai import AzureOpenAI
from dotenv import load_dotenv
from typing import Dict, Any

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
    prompt = f"""
I have a business report in JSON format that was generated from a website analysis.
Below is the report content:
{report_text}

Based on this report, please determine if the company is a vertical market software company.
Provide detailed reasoning for your decision and conclude with a final answer of either true or false.
Do not include any extra text before or after your JSON response.
Your response should be a valid JSON object with two keys:
- "reasoning": a string explaining your thought process,
- "final_answer": a boolean value that is either true or false.
"""
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
    
    system_message = (
        "You are an expert analyst using a reasoning model. "
        "Provide detailed reasoning and a final answer as a valid JSON object. "
        "The JSON must include 'reasoning' and 'final_answer' keys, with 'final_answer' being a boolean value (true or false)."
    )
    
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
    Loads the saved report from a JSON file and returns its content as a string.
    
    Args:
        filename (str): Path to the final report file.
        
    Returns:
        str: The contents of the report file.
        
    Raises:
        ValueError: If the file is not found or empty.
    """
    if not os.path.exists(filename):
        raise ValueError(f"Report file not found: {filename}")
    
    try:
        with open(filename, "r", encoding="utf-8") as f:
            report_data = json.load(f)
        report_text = json.dumps(report_data, indent=2)
        logger.info(f"Report loaded from {filename}.")
        return report_text
    except Exception as e:
        raise RuntimeError(f"Error loading report from {filename}: {str(e)}")

# -----------------------------------------------------------------------------
# Function: save_response
# -----------------------------------------------------------------------------
def save_response(response_data: Dict[str, Any], output_filename: str) -> None:
    """
    Saves the OpenAI response to a JSON file.
    
    Args:
        response_data (Dict[str, Any]): The JSON data to save.
        output_filename (str): The filename to save the response.
    """
    try:
        with open(output_filename, "w", encoding="utf-8") as f:
            json.dump(response_data, f, indent=4)
        logger.info(f"Response saved to {output_filename}")
    except Exception as e:
        raise RuntimeError(f"Failed to save response: {e}")

# -----------------------------------------------------------------------------
# Main function
# -----------------------------------------------------------------------------
def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(
        description="Analyze a business report and check if the company is a vertical market software company"
    )
    parser.add_argument("--report", type=str, default="final_website_report.json", help="Path to the final website report JSON file")
    parser.add_argument("--output", type=str, default="vertical_market_check_response.json", help="Output filename for the response")
    parser.add_argument("--retries", type=int, default=3, help="Number of retries for OpenAI API calls")
    args = parser.parse_args()
    
    try:
        logger.info("Loading report...")
        report_text = load_report(args.report)
    except Exception as e:
        logger.error(f"Error loading report: {e}")
        return
    
    # Build the prompt for vertical market check
    prompt = build_report_prompt(report_text)
    logger.debug("Built prompt for vertical market check.")
    
    try:
        logger.info("Sending prompt to OpenAI (o3-mini)...")
        response_data = send_prompt_to_openai(prompt, max_retries=args.retries)
    except Exception as e:
        logger.error(f"Error during OpenAI call: {e}")
        return
    
    try:
        logger.info("Saving response...")
        save_response(response_data, args.output)
    except Exception as e:
        logger.error(f"Error during saving response: {e}")
        return
    
    logger.info("Process completed successfully!")

if __name__ == '__main__':
    main()