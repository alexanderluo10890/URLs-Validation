from fastapi import APIRouter, HTTPException
from app.models.verticalMarketCheckModels import VerticalMarketCheckRequest, VerticalMarketCheckResponse
from app.services.verticalMarketChecker import build_report_prompt, send_prompt_to_openai

router = APIRouter()

@router.post("/vertical-market-check", response_model=VerticalMarketCheckResponse)
def vertical_market_check(request: VerticalMarketCheckRequest):
    """
    Endpoint to determine if a company is a vertical market software company based on a business report.
    The request should include the report text in JSON format.
    """
    try:
        # Build the prompt using the provided report text.
        prompt = build_report_prompt(request.report_text)
        
        # Send the prompt to Azure OpenAI and get the structured output.
        response_data = send_prompt_to_openai(prompt, max_retries=request.retries)
        
        # Validate that the response contains the expected keys.
        if "reasoning" not in response_data or "final_answer" not in response_data:
            raise ValueError("Invalid response from OpenAI API: missing 'reasoning' or 'final_answer'.")
        
        return VerticalMarketCheckResponse(
            reasoning=response_data["reasoning"],
            final_answer=response_data["final_answer"]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))