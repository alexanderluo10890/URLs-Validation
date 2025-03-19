from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from app.utils.validators import is_valid_url
from app.utils.firecrawlApp import crawl_website, load_scraped_website_content

router = APIRouter()

class WebsiteRequest(BaseModel):
    """Request model for website scraping."""
    url: str
    max_pages: Optional[int] = None
    force_crawl: bool = False

@router.post("/scrape")
def scrape_website(request: WebsiteRequest):
    """
    Endpoint to scrape a website.
    """
    try:
        # Validate URL
        is_valid, error_msg = is_valid_url(request.url)
        if not is_valid:
            raise ValueError(f"Invalid URL: {error_msg}")
        
        # Crawl the website
        filename, pages = crawl_website(request.url, page_limit=request.max_pages or 3)
        
        return {
            "message": "Website scraped successfully",
            "filename": filename,
            "pages_scraped": len(pages)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/load")
def load_scraped_content(max_pages: Optional[int] = None):
    """
    Endpoint to load scraped content.
    """
    try:
        pages_content = load_scraped_website_content(max_pages=max_pages or 3)
        if not pages_content:
            raise ValueError("No pages found to process.")
        
        return {
            "pages": pages_content,
            "total_pages": len(pages_content)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
