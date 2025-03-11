from fastapi import FastAPI
from app.routes.url_validation import router as url_validation_router

app = FastAPI()

# Include only the URL validation routes
app.include_router(url_validation_router, prefix="/validate-url", tags=["URL Validation"])

@app.get("/")
def root():
    return {"message": "Welcome to the URL Validation API"}
