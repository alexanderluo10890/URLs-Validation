from pydantic import BaseModel, HttpUrl, Field

class URLValidationRequest(BaseModel):
    """
    Represents the request body for the URL validation API.

    Attributes:
    - url (HttpUrl): The URL to validate and check for redirection.
    """
    url: HttpUrl = Field(..., description="The URL to validate")


class URLValidationResponse(BaseModel):
    """
    Represents the response body for the URL validation API.

    Attributes:
    - original_url (str): The full original URL provided in the request.
    - destination_url (str): The full final URL after following redirects.
    - original_domain (str): The domain extracted from the provided URL.
    - destination_domain (str): The domain of the final URL after redirection.
    - is_valid (bool): Indicates whether the URL format is valid.
    - is_redirected (bool): Indicates whether the URL was redirected to another domain.
    """
    original_url: str = Field(..., description="The full original URL provided in the request")
    destination_url: str = Field(..., description="The full final URL after following redirects")
    original_domain: str = Field(..., description="The original domain of the provided URL")
    destination_domain: str = Field(..., description="The final domain after redirection (if applicable)")
    is_valid: bool = Field(..., description="Indicates if the URL is valid")
    is_redirected: bool = Field(..., description="Indicates if the URL was redirected")
