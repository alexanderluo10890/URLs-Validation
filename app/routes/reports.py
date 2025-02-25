from fastapi import APIRouter, HTTPException
from app.services.openaiProcessor import (
    gather_scraped_content, 
    build_report_prompt, 
    send_prompt_to_openai, 
    parse_into_pydantic
)

router = APIRouter()

@router.get("/generate-report")
def generate_report_endpoint():
    try:
        # Step 1: Gather scraped website content (limit to 3 pages, or adjust as needed)
        pages_text = gather_scraped_content(max_pages=3)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error gathering scraped content: {e}")
    
    try:
        # Step 2: Build the report prompt using the scraped content
        system_prompt, user_prompt = build_report_prompt(pages_text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error building the prompt: {e}")
    
    try:
        # Step 3: Send the prompt to Azure OpenAI and receive raw JSON output
        raw_json = send_prompt_to_openai(user_prompt)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error from OpenAI: {e}")
    
    try:
        # Step 4: Parse the raw JSON into the Pydantic report model
        report_model = parse_into_pydantic(raw_json)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error parsing report JSON: {e}")
    
    return report_model.dict()
