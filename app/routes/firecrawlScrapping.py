from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from app.utils.validators import validate_url
from app.utils.firecrawlApp import gather_scraped_content
from fastapi.responses import JSONResponse
from fastapi import Request
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

class WebsiteRequest(BaseModel):
    """Request model for website scraping."""
    url: str
    max_pages: Optional[int] = None
    force_crawl: bool = False

@router.options("/scrape")
async def options_scrape():
    """Handle OPTIONS request for CORS preflight."""
    logger.info("Handling OPTIONS request for /scrape")
    return JSONResponse(
        content={},
        headers=CORS_HEADERS
    )

@router.post("/scrape")
async def scrape_website(request: WebsiteRequest):
    """
    Endpoint to scrape a website.
    """
    try:
        logger.info(f"Received POST request to /scrape with URL: {request.url}")
        logger.debug(f"Request body: {request.dict()}")
        
        # Validate URL
        is_valid, error_msg = validate_url(request.url)
        if not is_valid:
            logger.error(f"Invalid URL: {error_msg}")
            return JSONResponse(
                content={"detail": f"Invalid URL: {error_msg}"},
                status_code=400,
                headers=CORS_HEADERS
            )
        
        # Crawl the website
        logger.info("Starting website crawl")
        content = gather_scraped_content(url=request.url, max_pages=request.max_pages or 3, force_crawl=False)
        logger.info("Website crawl completed successfully")
        
        # Return with CORS headers
        return JSONResponse(
            content={
                "message": "Website scraped successfully",
                "content": content
            },
            headers=CORS_HEADERS
        )
    except Exception as e:
        logger.error(f"Error in scrape_website: {str(e)}", exc_info=True)
        return JSONResponse(
            content={"detail": str(e)},
            status_code=500,
            headers=CORS_HEADERS
        )

@router.options("/load")
async def options_load():
    """Handle OPTIONS request for CORS preflight."""
    logger.info("Handling OPTIONS request for /load")
    return JSONResponse(
        content={},
        headers=CORS_HEADERS
    )

@router.get("/load")
async def load_scraped_content(max_pages: Optional[int] = None):
    """
    Endpoint to load scraped content.
    """
    try:
        logger.info("Loading scraped content")
        pages_content = gather_scraped_content(max_pages=max_pages or 3)
        if not pages_content:
            logger.warning("No pages found to process")
            return JSONResponse(
                content={"detail": "No pages found to process."},
                status_code=404,
                headers=CORS_HEADERS
            )
        
        return JSONResponse(
            content={
                "pages": pages_content,
                "total_pages": len(pages_content)
            },
            headers=CORS_HEADERS
        )
    except Exception as e:
        logger.error(f"Error in load_scraped_content: {str(e)}", exc_info=True)
        return JSONResponse(
            content={"detail": str(e)},
            status_code=500,
            headers=CORS_HEADERS
        )
