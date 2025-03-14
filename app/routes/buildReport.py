from fastapi import APIRouter, HTTPException
from app.models.reportGenerationModels import ReportGenerationRequest, ReportGenerationResponse
from app.services.openaiProcessor import build_report_prompt, send_prompt_to_openai

router = APIRouter()

@router.post("/generate-report", response_model=ReportGenerationResponse)
def generate_report(request: ReportGenerationRequest):
    """
    Endpoint to generate a business report using OpenAI.
    It builds a prompt with the provided scraped pages content and then 
    calls the Azure OpenAI API to generate a report in JSON format.
    """
    try:
        # Build the prompt from scraped pages content
        prompt = build_report_prompt(request.pages_text)
        
        # Send the prompt to Azure OpenAI and get structured output
        report_data = send_prompt_to_openai(prompt, max_retries=request.retries)
        
        return ReportGenerationResponse(report=report_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))