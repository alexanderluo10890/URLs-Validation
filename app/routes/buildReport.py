from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
import json
import logging
import os
from urllib.parse import urlparse
from app.services.openaiProcessor import send_prompt_to_openai, parse_into_pydantic
from app.prompts.report_prompts import get_report_prompt

logger = logging.getLogger(__name__)

router = APIRouter()


class BuildReportRequest(BaseModel):
    pages_text: str
    retries: Optional[int] = 3
    url: Optional[str] = None


@router.post("/generate-report")
async def generate_report(request: BuildReportRequest):
    try:
        prompt = get_report_prompt(request.pages_text)
        data_dict = send_prompt_to_openai(prompt, max_retries=request.retries or 3)
        report_model = parse_into_pydantic(data_dict)
        report_dict = report_model.model_dump()

        if request.url:
            netloc = urlparse(request.url).netloc
            domain = (netloc[4:] if netloc.startswith('www.') else netloc).replace('.', '_')
            output_dir = os.path.join("output", domain)
            os.makedirs(output_dir, exist_ok=True)
            with open(os.path.join(output_dir, "report.json"), "w", encoding="utf-8") as f:
                json.dump(report_dict, f, indent=2, ensure_ascii=False)
            logger.info(f"Report saved to output/{domain}/report.json")

        return {"report": report_dict}
    except Exception as e:
        logger.error(f"Report generation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
