import re
import requests
from urllib.parse import urlparse, urljoin, quote, unquote
from fastapi import HTTPException
import idna

def validate_url(url: str):
    """
    Validates the URL format using a regex pattern and additional checks.
    Handles:
    - Scheme: http or https
    - Subdomain: Optional subdomain (e.g., www., api.)
    - Domain: The main domain including IDNs
    - TLD/STLD: Top-level or second-level domain
    - Path: Optional path with special characters
    - Query parameters and fragments
    """
    try:
        # First, try to parse the URL
        parsed = urlparse(url)
        
        # Check scheme
        if parsed.scheme not in ['http', 'https']:
            return False, "URL must use http or https scheme"
            
        # Handle IDN domains
        try:
            domain = parsed.netloc.encode('idna').decode('ascii')
        except (UnicodeError, idna.IDNAError):
            return False, "Invalid domain name"
            
        # Basic pattern for domain validation
        domain_pattern = re.compile(
            r'^'
            r'(([a-zA-Z0-9]|[a-zA-Z0-9][a-zA-Z0-9\-]*[a-zA-Z0-9])\.)*'  # subdomains
            r'([a-zA-Z0-9]|[a-zA-Z0-9][a-zA-Z0-9\-]*[a-zA-Z0-9])'       # main domain
            r'\.[a-zA-Z]{2,}'                                             # TLD
            r'(:[0-9]{1,5})?'                                            # optional port
            r'$'
        )
        
        if not domain_pattern.match(domain):
            return False, "Invalid domain format"
            
        # Validate and encode the path
        if parsed.path:
            encoded_path = quote(parsed.path, safe='/:')
            if not all(c.isprintable() for c in unquote(encoded_path)):
                return False, "Path contains invalid characters"
                
        return True, "Valid URL"
        
    except Exception as e:
        return False, f"Invalid URL: {str(e)}"

def check_redirection(url: str, timeout: int = 5):
    """
    Checks whether the given URL redirects to another domain.
    Handles:
    - Relative URLs in Location header
    - URL encoding/decoding
    - Various HTTP status codes
    - Timeouts and connection issues
    
    Parameters:
        url (str): The URL to check for redirection
        timeout (int): Timeout in seconds for each request (default: 5)
    
    Returns:
        original_domain (str): The domain of the original URL
        destination_domain (str): The domain of the final destination URL
        is_redirected (bool): Whether the URL was redirected to another domain
    """
    try:
        redirect_count = 0
        max_redirects = 4
        original_domain = urlparse(url).netloc
        current_url = url
        response = None
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

        while redirect_count < max_redirects:
            try:
                response = requests.get(
                    current_url,
                    allow_redirects=False,
                    timeout=timeout,
                    headers=headers
                )
                status_code = response.status_code

                # Handle different status codes
                if status_code == 404:
                    raise HTTPException(status_code=404, detail="URL not found (404)")
                elif status_code == 403:
                    raise HTTPException(status_code=403, detail="Access forbidden (403)")
                elif status_code == 401:
                    raise HTTPException(status_code=401, detail="Unauthorized access (401)")
                elif status_code >= 500:
                    raise HTTPException(status_code=status_code, detail=f"Server error ({status_code})")
                
                # Check for redirection status codes
                if status_code in [301, 302, 303, 307, 308]:
                    redirect_count += 1
                    location = response.headers.get("Location")
                    
                    if not location:
                        raise HTTPException(status_code=400, detail="Redirection URL is missing")
                        
                    # Handle relative URLs in Location header
                    current_url = urljoin(current_url, location)
                    
                    # Validate the new URL
                    is_valid, error_msg = validate_url(current_url)
                    if not is_valid:
                        raise HTTPException(status_code=400, detail=f"Invalid redirect URL: {error_msg}")
                else:
                    break

            except requests.Timeout:
                raise HTTPException(status_code=408, detail=f"Request timed out after {timeout} seconds")
            except requests.ConnectionError:
                raise HTTPException(status_code=400, detail="Failed to connect to the URL")

        # If maximum redirects are reached
        if redirect_count == max_redirects:
            raise HTTPException(status_code=400, detail="Too many redirects (max 4)")

        if response is None:
            raise HTTPException(status_code=400, detail="No response received from the server")

        # Get final destination domain
        destination_domain = urlparse(response.url).netloc
        
        # Check if redirection occurred to a different domain
        is_redirected = original_domain.lower() != destination_domain.lower()

        return original_domain, destination_domain, is_redirected

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error checking URL: {str(e)}") 