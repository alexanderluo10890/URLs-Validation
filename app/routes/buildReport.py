from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
import logging
from app.services.openaiProcessor import send_prompt_to_openai, parse_into_pydantic
from app.prompts.report_prompts import get_report_prompt

logger = logging.getLogger(__name__)

router = APIRouter()


class BuildReportRequest(BaseModel):
    pages_text: str
    retries: Optional[int] = 3


@router.post("/generate-report")
async def generate_report(request: BuildReportRequest):
    try:
        prompt = get_report_prompt(request.pages_text)
        data_dict = send_prompt_to_openai(prompt, max_retries=request.retries or 3)
        report_model = parse_into_pydantic(data_dict)
        logger.info("Report generated successfully")
        return {"report": report_model.model_dump()}
    except Exception as e:
        logger.error(f"Report generation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
