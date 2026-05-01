import json
import logging
import os
import time
from typing import Dict, Any
from pydantic import ValidationError
from openai import OpenAI
from dotenv import load_dotenv
from app.models.reportsModels import HighLevelBusinessWebsiteScrapeReport
from app.prompts.report_prompts import get_system_message

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
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": get_system_message()},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"},
                temperature=0,
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


def parse_into_pydantic(data_dict: Dict[str, Any]) -> HighLevelBusinessWebsiteScrapeReport:
    try:
        return HighLevelBusinessWebsiteScrapeReport(**data_dict)
    except ValidationError as e:
        raise ValueError(f"JSON does not match the Pydantic model: {e}")
