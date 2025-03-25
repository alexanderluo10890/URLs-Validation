from fastapi import APIRouter, HTTPException
from app.models.reportGenerationModels import ReportGenerationRequest, ReportGenerationResponse
from app.services.openaiProcessor2 import send_prompt_to_openai
from app.prompts.report_prompts import get_report_prompt
from fastapi.responses import JSONResponse
import logging
import json

# Set up logging
logger = logging.getLogger(__name__)

router = APIRouter()

# CORS headers
CORS_HEADERS = {
    "Access-Control-Allow-Origin": "http://localhost:5173",
    "Access-Control-Allow-Methods": "POST, OPTIONS, GET",
    "Access-Control-Allow-Headers": "Content-Type, Authorization",
    "Access-Control-Allow-Credentials": "true"
}

@router.options("/generate-report")
async def options_generate_report():
    """Handle OPTIONS request for CORS preflight."""
    logger.info("Handling OPTIONS request for /generate-report")
    return JSONResponse(
        content={},
        headers=CORS_HEADERS
    )

@router.post("/generate-report")
async def generate_report(request: ReportGenerationRequest):
    """
    Endpoint to generate a business report using OpenAI.
    It builds a prompt with the provided scraped pages content and then 
    calls the Azure OpenAI API to generate a report in JSON format.
    """
    try:
        logger.info("Received request to generate report")
        logger.debug(f"Request body: {request.dict()}")
        
        # Build the prompt from scraped pages content
        prompt = get_report_prompt(request.pages_text)
        
        # Send the prompt to Azure OpenAI and get structured output
        report_data = send_prompt_to_openai(prompt, max_retries=request.retries)
        
        # Log the response for debugging
        logger.debug(f"Generated report data: {json.dumps(report_data)[:500]}...")
        
        # Return with CORS headers
        return JSONResponse(
            content={"report": report_data},
            headers=CORS_HEADERS
        )
    except Exception as e:
        logger.error(f"Error generating report: {str(e)}", exc_info=True)
        # Return error with CORS headers
        return JSONResponse(
            content={"detail": str(e)},
            status_code=500,
            headers=CORS_HEADERS
        )