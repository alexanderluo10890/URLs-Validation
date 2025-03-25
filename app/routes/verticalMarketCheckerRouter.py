from fastapi import APIRouter, HTTPException
from app.models.verticalMarketCheckModels import VerticalMarketCheckRequest, VerticalMarketCheckResponse
from app.services.verticalMarketProcessor2 import build_report_prompt, send_prompt_to_openai
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

@router.options("/vertical-market-check")
async def options_vertical_market_check():
    """Handle OPTIONS request for CORS preflight."""
    logger.info("Handling OPTIONS request for /vertical-market-check")
    return JSONResponse(
        content={},
        headers=CORS_HEADERS
    )

@router.post("/vertical-market-check")
async def vertical_market_check(request: VerticalMarketCheckRequest):
    """
    Endpoint to determine if a company is a vertical market software company based on a business report.
    The request should include the report text in JSON format.
    """
    try:
        logger.info("Received request for vertical market check")
        logger.debug(f"Request body: {request.dict()}")
        
        # Build the prompt using the provided report text.
        prompt = build_report_prompt(request.report_text)
        
        # Send the prompt to Azure OpenAI and get the structured output.
        response_data = send_prompt_to_openai(prompt, max_retries=request.retries)
        
        # Log the raw response for debugging
        logger.debug(f"Raw OpenAI response: {json.dumps(response_data)}")
        
        # Validate that the response contains the expected keys.
        if "reasoning" not in response_data or "final_answer" not in response_data:
            logger.error("Invalid response from OpenAI API: missing keys")
            error_response = JSONResponse(
                content={"detail": "Invalid response from OpenAI API: missing 'reasoning' or 'final_answer'."},
                status_code=500,
                headers=CORS_HEADERS
            )
            return error_response
        
        # Convert final_answer to string if it's a boolean
        final_answer = response_data["final_answer"]
        if isinstance(final_answer, bool):
            final_answer = str(final_answer)
            logger.info(f"Converted boolean final_answer to string: {final_answer}")
        
        # Create the response with explicit CORS headers
        response_content = {
            "reasoning": response_data["reasoning"],
            "final_answer": final_answer
        }
        
        logger.info("Successfully processed vertical market check")
        logger.debug(f"Response content: {json.dumps(response_content)}")
        
        # Return JSON response with CORS headers
        return JSONResponse(
            content=response_content,
            headers=CORS_HEADERS
        )
    except Exception as e:
        logger.error(f"Error in vertical market check: {str(e)}", exc_info=True)
        # Return error response with CORS headers
        return JSONResponse(
            content={"detail": str(e)},
            status_code=500,
            headers=CORS_HEADERS
        )