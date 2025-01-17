from fastapi import APIRouter, HTTPException
from app.models.url_validation import URLValidationRequest, URLValidationResponse
from app.services.validators import is_valid_url, check_redirection
import logging

# Initialize router
router = APIRouter()

# Logger setup for error handling
logger = logging.getLogger("url_validation")
if not logger.hasHandlers():
    handler = logging.FileHandler("error.log")
    handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
    logger.addHandler(handler)
logger.setLevel(logging.ERROR)

@router.post("/", response_model=URLValidationResponse)
def validate_url(request: URLValidationRequest):
    """
    Route to validate a URL and determine its status.
    Handles validation and redirection checks.
    """
    try:
        # Explicitly convert HttpUrl to string
        url = str(request.url)
        
        # Step 1: Validate the URL format
        is_valid, message = is_valid_url(url)
        if not is_valid:
            return URLValidationResponse(
                original_url=url,
                destination_url=url,
                original_domain="Invalid domain",
                destination_domain="Invalid domain",
                is_valid=False,
                is_redirected=False,
            )
        
        # Step 2: Check for redirection
        original_domain, destination_domain, is_redirected = check_redirection(url)
        
        # Step 3: Construct the response
        return URLValidationResponse(
            original_url=url,
            destination_url=destination_domain if is_redirected else url,
            original_domain=original_domain,
            destination_domain=destination_domain,
            is_valid=True,
            is_redirected=is_redirected,
        )
    except HTTPException as e:
        raise e  # Rethrow known HTTP exceptions
    except Exception as e:
        # Log unexpected errors
        logger.error(f"Unexpected error for URL: {request.url} - {str(e)}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred. Please try again later.")
