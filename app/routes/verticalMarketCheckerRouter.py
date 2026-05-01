from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
import json
import logging
import os
from urllib.parse import urlparse
from app.services.verticalMarketProcessor import send_prompt_to_openai as vm_send_prompt
from app.prompts.vertical_market_prompts import get_vertical_market_prompt

logger = logging.getLogger(__name__)

router = APIRouter()


class VerticalMarketCheckRequest(BaseModel):
    report_text: str
    retries: Optional[int] = 3
    url: Optional[str] = None


@router.post("/vertical-market-check")
async def check_vertical_market(request: VerticalMarketCheckRequest):
    try:
        prompt = get_vertical_market_prompt(request.report_text)
        result = vm_send_prompt(prompt, max_retries=request.retries or 3)

        if request.url:
            netloc = urlparse(request.url).netloc
            domain = (netloc[4:] if netloc.startswith('www.') else netloc).replace('.', '_')
            output_dir = os.path.join("output", domain)
            os.makedirs(output_dir, exist_ok=True)
            with open(os.path.join(output_dir, "vertical_market_check.json"), "w", encoding="utf-8") as f:
                json.dump(result, f, indent=4)
            logger.info(f"Vertical market check saved to output/{domain}/vertical_market_check.json")

        return result
    except Exception as e:
        logger.error(f"Vertical market check error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
