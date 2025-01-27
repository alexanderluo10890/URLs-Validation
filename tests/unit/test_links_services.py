import pytest
from app.services.validators import is_valid_url, check_redirection
from urllib.parse import urlparse
from fastapi import HTTPException
from app.utils.file_operations import load_links

# Test URLs for various cases
TEST_URLS = {
    "with_www": "https://www.shopify.com/retail/retail-software",
    "without_www": "https://retailedge.com/",
    "with_tld_stld": "https://retailedge.com/",
    "with_subdomain": "https://www.shopify.com/retail/retail-software",
    "autodesk": "https://www.autodesk.com"
}

def test_is_valid_url():
    """Test the is_valid_url function with various URLs."""
    # Valid URLs
    for url in TEST_URLS.values():
        is_valid, message = is_valid_url(url)
        assert is_valid is True
        assert message == "Valid URL"

    # Invalid URLs
    invalid_urls = [
        "htt://missing-scheme.com",  # Invalid scheme
        "https://missing_tld",      # Missing TLD
        "https://.com",             # Missing domain
        "invalid-url"               # Invalid format
    ]
    for url in invalid_urls:
        is_valid, message = is_valid_url(url)
        assert is_valid is False
        assert "Invalid URL format" in message

def test_check_redirection():
    """Test the check_redirection function with various URLs."""
    # Valid and reachable URLs without redirection
    original_domain, destination_domain, is_redirected = check_redirection(TEST_URLS["autodesk"])
    assert original_domain == "www.autodesk.com"
    assert destination_domain == "www.autodesk.com"
    assert is_redirected is False

    # URLs with redirection (mocked to simulate)
    with pytest.raises(HTTPException) as excinfo:
        check_redirection("https://nonexistentdomain.xyz")
    assert excinfo.value.status_code == 404

def test_invalid_url_raises_http_exception():
    """Test that invalid URLs raise HTTPException."""
    with pytest.raises(HTTPException) as excinfo:
        check_redirection("http://invalid-url")
    assert excinfo.value.status_code == 400
    assert "Failed to connect to the URL." in str(excinfo.value)

def test_is_valid_url_with_edge_cases():
    """Test the is_valid_url function with edge cases."""
    edge_case_urls = [
        "https://subdomain.example.com",  # Subdomain
        "http://example.com:8080/path",  # With port and path
        "https://example.co.uk"       # STLD
    ]
    for url in edge_case_urls:
        print("**********", url)
        is_valid, message = is_valid_url(url)
        assert is_valid is True
        assert message == "Valid URL"
