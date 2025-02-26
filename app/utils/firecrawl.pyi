"""
Type stubs for firecrawl module.
"""

class FirecrawlApp:
    def __init__(self, api_key: str) -> None: ...
    def crawl_url(self, url: str, params: dict, poll_interval: int) -> dict: ... 