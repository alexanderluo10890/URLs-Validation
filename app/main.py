"""
Main entry point for the application that connects all the functionality.
"""

import argparse
import json
import logging
from typing import Optional
from app.services.openaiProcessor import send_prompt_to_openai, parse_into_pydantic
from app.services.verticalMarketProcessor import load_report, save_response
from app.utils.firecrawlApp import crawl_website, load_scraped_website_content
from app.utils.validators import validate_url as validate_url_util
from app.prompts.report_prompts import get_report_prompt
from app.prompts.vertical_market_prompts import get_vertical_market_prompt
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from app.routes.reports import router as reports_router
from app.routes.firecrawlScrapping import router as firecrawl_scrapping_router
from app.routes.buildReport import router as build_report_router
from app.routes.verticalMarketCheckerRouter import router as vertical_market_checker_router
import uvicorn

# -----------------------------------------------------------------------------
# Logging Setup
# -----------------------------------------------------------------------------
logging.basicConfig(
    level=logging.DEBUG,  # Changed to DEBUG for more detailed logging
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

# -----------------------------------------------------------------------------
# FastAPI Setup
# -----------------------------------------------------------------------------
app = FastAPI(
    title="Business Website Analysis API",
    description="API for analyzing business websites and determining if they are vertical market software companies",
    version="1.0.0"
)

# -----------------------------------------------------------------------------
# CORS Configuration
# -----------------------------------------------------------------------------
origins = [
    "http://localhost",
    "http://localhost:3000",  # React default port
    "http://localhost:5173",  # Vite default port
    "http://localhost:8000",  # FastAPI default port
    "http://127.0.0.1:3000",
    "http://127.0.0.1:5173",  # Vite default port
    "http://127.0.0.1:8000",
]

logger.info(f"Configuring CORS with allowed origins: {origins}")

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["*"],
    expose_headers=["*"],
    max_age=3600,  # Cache preflight requests for 1 hour
)

# -----------------------------------------------------------------------------
# Request Logging Middleware
# -----------------------------------------------------------------------------
@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.debug(f"Request: {request.method} {request.url}")
    logger.debug(f"Headers: {dict(request.headers)}")
    logger.debug(f"Origin: {request.headers.get('origin')}")
    
    response = await call_next(request)
    
    logger.debug(f"Response status: {response.status_code}")
    logger.debug(f"Response headers: {dict(response.headers)}")
    return response

# -----------------------------------------------------------------------------
# Register Routers
# -----------------------------------------------------------------------------
logger.info("Registering API routers...")
app.include_router(reports_router, prefix="/api/reports", tags=["Reports"])
app.include_router(firecrawl_scrapping_router, prefix="/api/scrape", tags=["Firecrawl Scraping"])
app.include_router(build_report_router, prefix="/api/report", tags=["Report Generation"])
app.include_router(vertical_market_checker_router, prefix="/api/vertical-market-check", tags=["Vertical Market Check"])

def validate_url(url: str) -> bool:
    """
    Validates if the provided string is a valid URL.
    
    Args:
        url (str): The URL to validate
        
    Returns:
        bool: True if the URL is valid, False otherwise
    """
    is_valid, _ = validate_url_util(url)
    return is_valid

def gather_scraped_content(url: Optional[str] = None, max_pages: Optional[int] = None, force_crawl: bool = False) -> str:
    """
    Loads the scraped website content and returns a single string containing the content of the pages.
    
    Args:
        url (Optional[str], optional): URL to crawl if provided. Defaults to None.
        max_pages (Optional[int], optional): Maximum number of pages to process. Defaults to None.
        force_crawl (bool, optional): Force a new crawl even if data exists. Defaults to False.
    
    Returns:
        str: Joined text content from all scraped pages
        
    Raises:
        ValueError: If the URL is invalid or no pages are found to process
        RuntimeError: If there's an error during crawling
    """
    if url:
        # Validate URL
        if not validate_url(url):
            raise ValueError(f"Invalid URL format: {url}")
        
        # Check if we need to crawl the website
        if force_crawl:
            logger.info(f"Crawling website: {url}")
            try:
                scraped_filename, _ = crawl_website(url, page_limit=max_pages or 3)
            except Exception as e:
                raise RuntimeError(f"Failed to crawl website {url}: {str(e)}")
    
    # Load the content from the file
    try:
        pages_content = load_scraped_website_content(max_pages=int(max_pages or 3))
        if not pages_content:
            raise ValueError("No pages found to process.")
        
        joined_text = "\n\n---PAGE BREAK---\n\n".join(pages_content)
        return joined_text
    except FileNotFoundError:
        raise ValueError("No scraped data found. Please make sure the website has been crawled.")
    except Exception as e:
        raise RuntimeError(f"Error loading content: {str(e)}")

def save_report_to_json(report_model, filename: str = "final_website_report.json") -> None:
    """
    Save the report model to a JSON file.
    
    Args:
        report_model: The report model to save
        filename: The name of the file to save to
    """
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(report_model.model_dump(), f, indent=2, ensure_ascii=False)
        logger.info(f"Report saved to {filename}")
    except Exception as e:
        logger.error(f"Error saving report to JSON: {e}")
        raise

def generate_website_report(url: str, max_pages: Optional[int] = None, force_crawl: bool = False) -> None:
    """
    Generate a business report from a website.
    
    Args:
        url (str): The URL of the website to analyze
        max_pages (Optional[int]): Maximum number of pages to process
        force_crawl (bool): Whether to force a new crawl
    """
    try:
        # Gather content from the website
        content = gather_scraped_content(url, max_pages, force_crawl)
        
        # Get the report prompt
        prompt = get_report_prompt(content)
        
        # Send to OpenAI and get response
        data_dict = send_prompt_to_openai(prompt)
        
        # Parse into Pydantic model
        report_model = parse_into_pydantic(data_dict)
        
        # Save the report
        save_report_to_json(report_model)
        
        logger.info("Report generation completed successfully")
    except Exception as e:
        logger.error(f"Error generating report: {e}")
        raise

def analyze_vertical_market(report_file: str, output_file: str, retries: int = 3) -> None:
    """
    Analyze a business report to determine if the company is a vertical market software company.
    
    Args:
        report_file (str): Path to the final website report JSON file
        output_file (str): Output filename for the response
        retries (int, optional): Number of retries for OpenAI API calls. Defaults to 3.
    """
    try:
        logger.info("Loading report...")
        report_text = load_report(report_file)
    except Exception as e:
        logger.error(f"Error loading report: {e}")
        return
    
    try:
        # Build the prompt for vertical market check
        prompt = get_vertical_market_prompt(report_text)
        logger.debug("Built prompt for vertical market check.")
        
        # Send to OpenAI
        logger.info("Sending prompt to OpenAI (o3-mini)...")
        response_data = send_prompt_to_openai(prompt, max_retries=retries)
        
        # Save the response
        logger.info("Saving response...")
        save_response(response_data, output_file)
        
        logger.info("Process completed successfully!")
    except Exception as e:
        logger.error(f"Error during analysis: {e}")

def main():
    """
    Main entry point for the application.
    """
    parser = argparse.ArgumentParser(description="Business Website Analysis Tool")
    parser.add_argument("--mode", choices=["api", "cli"], default="api", help="Run mode: api (FastAPI server) or cli (command line)")
    parser.add_argument("--url", type=str, help="URL to analyze (for CLI mode)")
    parser.add_argument("--max-pages", type=int, default=3, help="Maximum number of pages to process")
    parser.add_argument("--force-crawl", action="store_true", help="Force a new crawl even if data exists")
    parser.add_argument("--report", type=str, default="final_website_report.json", help="Path to the report file")
    parser.add_argument("--output", type=str, default="vertical_market_check_response.json", help="Output filename for the response")
    parser.add_argument("--retries", type=int, default=3, help="Number of retries for OpenAI API calls")
    parser.add_argument("--host", type=str, default="0.0.0.0", help="Host to run the API server on")
    parser.add_argument("--port", type=int, default=8000, help="Port to run the API server on")
    args = parser.parse_args()
    
    if args.mode == "api":
        logger.info(f"Starting API server on {args.host}:{args.port}")
        uvicorn.run(app, host=args.host, port=args.port)
    else:
        if not args.url:
            logger.error("URL is required for CLI mode")
            return
        
        try:
            generate_website_report(args.url, args.max_pages, args.force_crawl)
            analyze_vertical_market(args.report, args.output, args.retries)
            logger.info("Process completed successfully!")
        except Exception as e:
            logger.error(f"Error during processing: {e}")
            return

if __name__ == "__main__":
    main()
