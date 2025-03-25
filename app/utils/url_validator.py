from pydantic import HttpUrl
from app.models.url_validation import URLValidationResponse
from app.utils.validators import validate_url, check_redirection
import logging

# Logger setup for error handling
logger = logging.getLogger("url_validation")
if not logger.hasHandlers():
    handler = logging.FileHandler("error.log")
    handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
    logger.addHandler(handler)
logger.setLevel(logging.ERROR)

def is_valid_url(url: HttpUrl) -> URLValidationResponse:
    """
    Validate a URL and determine its status.
    Handles validation and redirection checks.
    
    Args:
        url (HttpUrl): The URL to validate
        
    Returns:
        URLValidationResponse: The validation result
    """
    try:
        # Explicitly convert HttpUrl to string
        url_str = str(url)
        
        # Step 1: Validate the URL format
        is_valid, message = validate_url(url_str)
        if not is_valid:
            return URLValidationResponse(
                original_url=url_str,
                destination_url=url_str,
                original_domain="Invalid domain",
                destination_domain="Invalid domain",
                is_valid=False,
                is_redirected=False,
            )
        
        # Step 2: Check for redirection
        original_domain, destination_domain, is_redirected = check_redirection(url_str)
        
        # Step 3: Construct the response
        return URLValidationResponse(
            original_url=url_str,
            destination_url=destination_domain if is_redirected else url_str,
            original_domain=original_domain,
            destination_domain=destination_domain,
            is_valid=True,
            is_redirected=is_redirected,
        )
    except Exception as e:
        # Log unexpected errors
        logger.error(f"Unexpected error for URL: {url} - {str(e)}")
        raise 