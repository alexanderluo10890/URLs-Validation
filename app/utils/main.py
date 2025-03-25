from fastapi import FastAPI
from fastapi.responses import FileResponse
import uvicorn
import os

# Import all routers
from app.routes.firecrawlScrapping import router as firecrawl_scrapping_router
from app.routes.buildReport import router as build_report_router
from app.routes.verticalMarketCheckerRouter import router as vertical_market_checker_router

def create_app() -> FastAPI:
    """
    Factory function to create and configure the FastAPI application.
    """
    app = FastAPI(
        title="Business Website Analysis API",
        description="API for analyzing business websites and determining if they are vertical market software companies",
        version="1.0.0"
    )

    # Include all routers
    app.include_router(firecrawl_scrapping_router, prefix="/api/scrape", tags=["Firecrawl Scraping"])
    app.include_router(build_report_router, prefix="/api/report", tags=["Report Generation"])
    app.include_router(vertical_market_checker_router, prefix="/api/vertical-market-check", tags=["Vertical Market Check"])

    # Simple root route
    @app.get("/", tags=["Root"])
    def root():
        """
        Root endpoint that provides a welcome message.
        """
        return {
            "message": "Welcome to the Business Website Analysis API!",
            "available_endpoints": {
                "Scraping": "/api/scrape",
                "Report Generation": "/api/report",
                "Vertical Market Check": "/api/vertical-market-check"
            }
        }

    # Serve the favicon.ico file
    @app.get("/favicon.ico", include_in_schema=False)
    def favicon():
        """
        Serve the favicon.ico file.
        """
        file_path = os.path.join("app", "static", "favicon.ico")
        if os.path.exists(file_path):
            return FileResponse(file_path)
        return {"error": "Favicon not found"}

    return app

app = create_app()

if __name__ == "__main__":
    uvicorn.run(
        "app.utils.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
