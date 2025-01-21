import pytest
from pydantic import ValidationError, HttpUrl
from app.models.url_validation import URLValidationRequest, URLValidationResponse

# Test data for URL validation
VALID_URLS = [
    "https://www.shopify.com/retail/retail-software",
    "https://retailedge.com/",
    "https://www.autodesk.com",
    "https://subdomain.example.com",
    "http://example.com:8080/path"
]

INVALID_URLS = [
    "htt://missing-scheme.com",  # Invalid scheme
    "https://missing_tld",      # Missing TLD
    "https://.com",             # Missing domain
    "invalid-url"               # Invalid format
]

def test_url_validation_request_valid_urls():
    """Test URLValidationRequest model with valid URLs."""
    for url in VALID_URLS:
        request = URLValidationRequest(url=HttpUrl(url))
        assert request.url == url

def test_url_validation_request_invalid_urls():
    """Test URLValidationRequest model with invalid URLs."""
    for url in INVALID_URLS:
        with pytest.raises(ValidationError) as excinfo:
            URLValidationRequest(url=HttpUrl(url))
        assert "value is not a valid URL" in str(excinfo.value)

def test_url_validation_response_valid():
    """Test URLValidationResponse model with valid data."""
    response = URLValidationResponse(
        original_url=VALID_URLS[0],
        destination_url=VALID_URLS[1],
        original_domain="www.shopify.com",
        destination_domain="retailedge.com",
        is_valid=True,
        is_redirected=True
    )
    assert response.original_url == VALID_URLS[0]
    assert response.destination_url == VALID_URLS[1]
    assert response.original_domain == "www.shopify.com"
    assert response.destination_domain == "retailedge.com"
    assert response.is_valid is True
    assert response.is_redirected is True

def test_url_validation_response_missing_field():
    """Test URLValidationResponse with missing fields raises ValidationError."""
    with pytest.raises(ValidationError) as excinfo:
        URLValidationResponse(
            original_url=VALID_URLS[0],
            destination_url=None,  # Missing destination_url # type: ignore
            original_domain="www.shopify.com",
            destination_domain="retailedge.com",
            is_valid=True,
            is_redirected=True
        )
    assert "field required" in str(excinfo.value)

