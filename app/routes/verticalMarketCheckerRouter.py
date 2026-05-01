from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
import logging
from app.services.verticalMarketProcessor import send_prompt_to_openai as vm_send_prompt
from app.prompts.vertical_market_prompts import get_vertical_market_prompt

logger = logging.getLogger(__name__)

router = APIRouter()


class VerticalMarketCheckRequest(BaseModel):
    report_text: str
    retries: Optional[int] = 3


@router.post("/vertical-market-check")
async def check_vertical_market(request: VerticalMarketCheckRequest):
    try:
        prompt = get_vertical_market_prompt(request.report_text)
        result = vm_send_prompt(prompt, max_retries=request.retries or 3)
        logger.info("Vertical market check completed")
        return result
    except Exception as e:
        logger.error(f"Vertical market check error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
