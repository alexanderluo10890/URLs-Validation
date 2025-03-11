# File: app/utils/main.py

from fastapi import FastAPI
import uvicorn

# Import your routers from the routes folder
from app.routes.url_validation import router as url_validation_router
from app.routes.firecrawlScrapping import router as firecrawl_scrapping_router
from app.routes.buildReport import router as build_report_router
from app.routes.verticalMarketCheckerRouter import router as vertical_market_checker_router

def create_app() -> FastAPI:
    """
    Factory function to create and configure the FastAPI application.
    """
    app = FastAPI(title="My API")

    # Include your routers here
    app.include_router(url_validation_router, prefix="/validate", tags=["URL Validation"])
    app.include_router(firecrawl_scrapping_router, prefix="/scrape", tags=["Firecrawl Scraping"])
    app.include_router(build_report_router, prefix="/report", tags=["Report Generation"])
    app.include_router(vertical_market_checker_router, prefix="/vertical-market-check", tags=["Vertical Market Check"])

    return app

app = create_app()

if __name__ == "__main__":
    uvicorn.run(
        app,
        host="0.0.0.0",  # or "127.0.0.1" for local development
        port=8000,
        reload=True      # Set to True for auto-reload in development
    )
