import re
import requests
from urllib.parse import urlparse
from fastapi import HTTPException

def is_valid_url(url: str):
    """
    Validates the URL format using a regex pattern.
    The pattern checks:
    - Scheme: http or https
    - Subdomain: Optional subdomain (e.g., www., api.)
    - Domain: The main domain (e.g., example)
    - TLD/STLD: Top-level or second-level domain (e.g., .com, .co.uk)
    - Path: Optional path after the domain
    """
    # Regex to validate URL format
    pattern = re.compile(
        r'^(http|https)://'                     # Scheme (http or https)
        r'((www\.)?'                            # Optional 'www.' or null (no subdomain)
        r'(([a-zA-Z0-9-]+)\.)*'                 # Optional subdomains (e.g., sub.example.com)
        r'([a-zA-Z0-9-]+))'                     # Main domain (e.g., example)
        r'(\.[a-zA-Z]{2,})'                     # TLD/STLD (e.g., .com, .co.uk)
        r'(:[0-9]{1,5})?'                       # Optional port (e.g., :8080)
        r'(/.*)?$'                              # Optional path (e.g., /path/to/resource)
    )
    if not pattern.match(url):
        return False, (
            "Invalid URL format. Ensure the URL starts with http:// or https://, "
            "and includes a valid domain and TLD/STLD."
        )
    return True, "Valid URL"

def check_redirection(url: str):
    """
    Checks whether the given URL redirects to another domain.
    Returns the original domain, destination domain, and a boolean indicating if redirection occurred.
    
    Parameters:
        url (str): The URL to check for redirection.

    Returns:
        original_domain (str): The domain of the original URL.
        destination_domain (str): The domain of the final destination URL (after redirection, if any).
        is_redirected (bool): Whether the URL was redirected to another domain.
    """
    try:
        # Send a GET request to follow redirects (timeout set for better error handling)
        response = requests.get(url, allow_redirects=True, timeout=10)
        
        # Extract domains using urlparse
        original_domain = urlparse(url).netloc
        destination_domain = urlparse(response.url).netloc
        
        # Check if redirection occurred
        is_redirected = original_domain != destination_domain
        
        return original_domain, destination_domain, is_redirected

    except requests.exceptions.Timeout:
        raise HTTPException(status_code=408, detail="Request timed out while trying to reach the URL.")
    except requests.exceptions.ConnectionError:
        raise HTTPException(status_code=400, detail="Failed to connect to the URL. Check if the URL is reachable.")
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=400, detail=f"Error reaching the URL: {str(e)}")

    
    # def is_valid_url(url):
    # """
    # Validates the URL format using a regex pattern.
    # """
    # pattern = re.compile(
    #     r'^(http|https)://'                     # Scheme (http or https)
    #     r'(([a-zA-Z0-9.-]+)\.([a-zA-Z]{2,}))'  # Domain name
    #     r'(:[0-9]{1,5})?'                      # Optional port
    #     r'(/.*)?$'                             # Optional path
    #     #sub domain
    #     #www. or nothttp:// or https://
    #     # www. or null
    #     # check for subdomain
    #     # domain
    #     # check tld or stld 
    #     # then strip path .com 
    #     # .us.com
    #     # .co.uk
    # )
    # if not pattern.match(url):
    #     return False, "Invalid URL format. Ensure the URL starts with http:// or https:// and includes a valid domain."
    # return True, "Valid URL"
