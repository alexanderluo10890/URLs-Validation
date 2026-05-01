import json
import os
import time
import argparse
import logging
from openai import OpenAI
from dotenv import load_dotenv
from typing import Dict, Any
from app.prompts.vertical_market_prompts import get_vertical_market_prompt, get_vertical_market_system_message

load_dotenv()

logger = logging.getLogger(__name__)

client = OpenAI(api_key=os.getenv('OPENAI_API_KEY', ''))


def send_prompt_to_openai(prompt: str, max_retries: int = 3, retry_delay: int = 5) -> Dict[str, Any]:
    attempt = 0
    last_error = None

    while attempt < max_retries:
        try:
            logger.info(f"Sending request to OpenAI (attempt {attempt + 1}/{max_retries})")
            response = client.chat.completions.create(
                model="o3-mini",
                messages=[
                    {"role": "system", "content": get_vertical_market_system_message()},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"}
            )

            raw = response.choices[0].message.content
            if not raw or not raw.strip():
                raise ValueError("OpenAI returned an empty response")

            try:
                data_dict: Dict[str, Any] = json.loads(raw)
                logger.info("Successfully received and parsed JSON response")
                return data_dict
            except json.JSONDecodeError as e:
                raise ValueError(f"Failed to parse JSON response: {str(e)}")

        except Exception as e:
            last_error = e
            attempt += 1
            logger.error(f"Attempt {attempt}/{max_retries} failed: {str(e)}")
            if attempt < max_retries:
                time.sleep(retry_delay)

    raise RuntimeError(f"OpenAI API Error after {max_retries} attempts: {str(last_error)}")


def load_report(filename: str) -> str:
    if not os.path.exists(filename):
        raise ValueError(f"Report file not found: {filename}")
    try:
        with open(filename, "r", encoding="utf-8") as f:
            report_data = json.load(f)
        return json.dumps(report_data, indent=2)
    except Exception as e:
        raise RuntimeError(f"Error loading report from {filename}: {str(e)}")


def save_response(response_data: Dict[str, Any], output_filename: str) -> None:
    try:
        with open(output_filename, "w", encoding="utf-8") as f:
            json.dump(response_data, f, indent=4)
        logger.info(f"Response saved to {output_filename}")
    except Exception as e:
        raise RuntimeError(f"Failed to save response: {e}")


def main():
    parser = argparse.ArgumentParser(description="Check if a company is a vertical market software company")
    parser.add_argument("--report", type=str, default="final_website_report.json")
    parser.add_argument("--output", type=str, default="vertical_market_check_response.json")
    parser.add_argument("--retries", type=int, default=3)
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s [%(levelname)s] %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    try:
        report_text = load_report(args.report)
        prompt = get_vertical_market_prompt(report_text)
        response_data = send_prompt_to_openai(prompt, max_retries=args.retries)
        save_response(response_data, args.output)
        logger.info("Process completed successfully!")
    except Exception as e:
        logger.error(f"Error: {e}")


if __name__ == '__main__':
    main()
