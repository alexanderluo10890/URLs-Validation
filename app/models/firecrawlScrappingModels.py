from pydantic import BaseModel, HttpUrl

class FirecrawlScrapeRequest(BaseModel):
    url: HttpUrl
    max_pages: int = 3
    force_crawl: bool = False

class FirecrawlScrapeResponse(BaseModel):
    scraped_content: str
    source_file: str
