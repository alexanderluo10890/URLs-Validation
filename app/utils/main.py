from fastapi import FastAPI
from fastapi.responses import FileResponse
import uvicorn
import os

# Import all routers
from app.routes.url_validation import router as url_validation_router
from app.routes.firecrawlScrapping import router as firecrawl_scrapping_router
from app.routes.buildReport import router as build_report_router
from app.routes.verticalMarketCheckerRouter import router as vertical_market_checker_router

def create_app() -> FastAPI:
    """
    Factory function to create and configure the FastAPI application.
    """
    app = FastAPI(title="My API")

    # Include all routers
    app.include_router(url_validation_router, prefix="/validate", tags=["URL Validation"])
    app.include_router(firecrawl_scrapping_router, prefix="/scrape", tags=["Firecrawl Scraping"])
    app.include_router(build_report_router, prefix="/report", tags=["Report Generation"])
    app.include_router(vertical_market_checker_router, prefix="/vertical-market-check", tags=["Vertical Market Check"])

    # Simple root route
    @app.get("/")
    def root():
        return {"message": "Welcome to the Full API with multiple services!"}

    # Serve the favicon.ico file
    @app.get("/favicon.ico", include_in_schema=False)
    def favicon():
        file_path = os.path.join("app", "static", "favicon.ico")
        return FileResponse(file_path)

    return app

app = create_app()

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
