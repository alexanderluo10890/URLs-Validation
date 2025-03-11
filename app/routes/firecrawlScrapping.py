from fastapi import APIRouter, HTTPException
import os
from urllib.parse import urlparse
from app.services.openaiProcessor import validate_url 
from app.utils.firecrawlApp import crawl_website, load_scraped_website_content  
from app.models.firecrawlScrappingModels import FirecrawlScrapeRequest, FirecrawlScrapeResponse

router = APIRouter()

@router.post("/", response_model=FirecrawlScrapeResponse)
def firecrawl_scrape(request: FirecrawlScrapeRequest):
    """
    Endpoint to perform website scraping using Firecrawl.
    Validates the URL, triggers a crawl if needed, and returns the scraped content.
    """
    try:
        # Validate URL using helper from openaiProcessor.py
        if not validate_url(str(request.url)):
            raise HTTPException(status_code=400, detail="Invalid URL format.")
        
        # Generate a filename based on the URL's domain
        parsed = urlparse(str(request.url))
        domain = parsed.netloc
        if domain.startswith("www."):
            domain = domain[4:]
        domain_filename = domain.replace(".", "_")
        filename = f"{domain_filename}_scraped_data.json"
        
        # If force_crawl is True or the file doesn't exist, perform a crawl
        if request.force_crawl or not os.path.exists(filename):
            scraped_filename, _ = crawl_website(str(request.url), page_limit=request.max_pages) 
            filename = scraped_filename
        
        # Load scraped content from the generated file
        pages = load_scraped_website_content(filename=filename, max_pages=request.max_pages)  
        if not pages:
            raise HTTPException(status_code=404, detail="No pages found to scrape.")
        
        scraped_content = "\n\n---PAGE BREAK---\n\n".join(pages)
        return FirecrawlScrapeResponse(scraped_content=scraped_content, source_file=filename)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
