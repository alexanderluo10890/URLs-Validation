from fastapi import APIRouter, HTTPException
from app.models.reportGenerationModels import ReportGenerationRequest, ReportGenerationResponse
from app.services.openaiProcessor import send_prompt_to_openai, parse_into_pydantic
from app.prompts.report_prompts import get_report_prompt
from app.utils.firecrawlApp import load_scraped_website_content

router = APIRouter()

@router.get("/generate-report")
def generate_report_endpoint():
    """
    Endpoint to generate a report from scraped content.
    This endpoint automatically scrapes content and generates a report.
    """
    try:
        # Step 1: Gather scraped website content (limit to 3 pages)
        pages_content = load_scraped_website_content(max_pages=3)
        if not pages_content:
            raise ValueError("No pages found to process.")
        pages_text = "\n\n---PAGE BREAK---\n\n".join(pages_content)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error gathering scraped content: {e}")
    
    try:
        # Step 2: Build the report prompt using the scraped content
        prompt = get_report_prompt(pages_text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error building the prompt: {e}")
    
    try:
        # Step 3: Send the prompt to Azure OpenAI and receive raw JSON output
        raw_json = send_prompt_to_openai(prompt)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error from OpenAI: {e}")
    
    try:
        # Step 4: Parse the raw JSON into the Pydantic report model
        report_model = parse_into_pydantic(raw_json)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error parsing report JSON: {e}")
    
    return report_model.dict()

@router.post("/generate-report", response_model=ReportGenerationResponse)
def generate_report_from_text(request: ReportGenerationRequest):
    """
    Endpoint to generate a business report using OpenAI.
    It builds a prompt with the provided text content and then 
    calls the Azure OpenAI API to generate a report in JSON format.
    """
    try:
        # Build the prompt from provided text content
        prompt = get_report_prompt(request.pages_text)
        
        # Send the prompt to Azure OpenAI and get structured output
        report_data = send_prompt_to_openai(prompt, max_retries=request.retries)
        
        return ReportGenerationResponse(report=report_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
