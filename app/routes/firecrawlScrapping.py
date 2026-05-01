from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
import logging
import os
from urllib.parse import urlparse
from app.utils.firecrawlApp import crawl_website, load_scraped_website_content

logger = logging.getLogger(__name__)

router = APIRouter()


class ScrapeRequest(BaseModel):
    url: str
    max_pages: Optional[int] = 3
    force_crawl: Optional[bool] = False


@router.options("/scrape")
async def options_scrape():
    return {"status": "ok"}


@router.post("/scrape")
async def scrape_website(request: ScrapeRequest):
    try:
        url = request.url
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url

        netloc = urlparse(url).netloc
        domain = (netloc[4:] if netloc.startswith('www.') else netloc).replace('.', '_')
        output_dir = os.path.join("output", domain)
        os.makedirs(output_dir, exist_ok=True)

        deduplicated_file = os.path.join(output_dir, "deduplicated_data.json")

        if request.force_crawl or not os.path.exists(deduplicated_file):
            logger.info(f"Crawling website: {url}")
            crawl_website(url, page_limit=request.max_pages or 3, output_dir=output_dir)

        pages = load_scraped_website_content(filename=deduplicated_file, max_pages=request.max_pages or 3)
        if not pages:
            raise HTTPException(status_code=422, detail="No content found after scraping.")

        content = "\n\n---PAGE BREAK---\n\n".join(pages)
        logger.info(f"Scraping completed for {url}")
        return {"message": "Content loaded successfully", "content": content}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Scraping error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
