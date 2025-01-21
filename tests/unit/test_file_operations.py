import requests
import json
import pytest
from unittest.mock import patch

# Mocked JSON data for testing
MOCK_LINKS = {
    "links": [
        "https://www.example.com",
        "http://invalid-url",
        "https://nonexistentdomain.xyz"
    ]
}

def test_link(url):
    """
    Tests a single URL for reachability.

    Args:
        url (str): The URL to test.

    Returns:
        dict: A dictionary with the URL, status code, and reachability status.
    """
    try:
        response = requests.head(url, allow_redirects=True, timeout=5)
        return {
            "url": url,
            "status_code": response.status_code,
            "is_reachable": response.ok,
        }
    except requests.exceptions.RequestException as e:
        return {
            "url": url,
            "status_code": None,
            "is_reachable": False,
            "error": str(e),
        }

def test_links(urls):
    """
    Tests a list of URLs for reachability.

    Args:
        urls (list): A list of URLs to test.

    Returns:
        list: A list of dictionaries with test results for each URL.
    """
    return [test_link(url) for url in urls]

@pytest.fixture
def mock_json_file(tmp_path):
    """Fixture to create a temporary JSON file with mock links."""
    file_path = tmp_path / "mock_links.json"
    with open(file_path, "w") as f:
        json.dump(MOCK_LINKS, f)
    return file_path

def test_valid_url_success():
    """Test a valid URL returns correct status."""
    with patch("requests.head") as mock_head:
        mock_head.return_value.status_code = 200
        mock_head.return_value.ok = True
        result = test_link("https://www.example.com")
        assert result["url"] == "https://www.example.com"
        assert result["status_code"] == 200
        assert result["is_reachable"] is True

def test_invalid_url_format():
    """Test an invalid URL format raises an error."""
    with patch("requests.head") as mock_head:
        mock_head.side_effect = requests.exceptions.InvalidURL("Invalid URL format")
        result = test_link("http://invalid-url")
        assert result["url"] == "http://invalid-url"
        assert result["status_code"] is None
        assert result["is_reachable"] is False
        assert "error" in result

def test_unreachable_url():
    """Test a valid but unreachable URL."""
    with patch("requests.head") as mock_head:
        mock_head.side_effect = requests.exceptions.ConnectionError("Connection error")
        result = test_link("https://nonexistentdomain.xyz")
        assert result["url"] == "https://nonexistentdomain.xyz"
        assert result["status_code"] is None
        assert result["is_reachable"] is False
        assert "error" in result

def test_test_links_function():
    """Test the function that processes all links from a list."""
    with patch("requests.head") as mock_head:
        mock_head.side_effect = [
            type("Response", (object,), {"status_code": 200, "ok": True}),
            requests.exceptions.InvalidURL("Invalid URL format"),
            requests.exceptions.ConnectionError("Connection error"),
        ]
        links = ["https://www.example.com", "http://invalid-url", "https://nonexistentdomain.xyz"]
        results = test_links(links)

        assert results[0]["url"] == "https://www.example.com"
        assert results[0]["status_code"] == 200
        assert results[0]["is_reachable"] is True

        assert results[1]["url"] == "http://invalid-url"
        assert results[1]["status_code"] is None
        assert results[1]["is_reachable"] is False
        assert "error" in results[1]

        assert results[2]["url"] == "https://nonexistentdomain.xyz"
        assert results[2]["status_code"] is None
        assert results[2]["is_reachable"] is False
        assert "error" in results[2]

def test_save_results_to_json(tmp_path):
    """Test saving results to a JSON file."""
    output_file = tmp_path / "results.json"
    results = [
        {"url": "https://www.example.com", "status_code": 200, "is_reachable": True},
        {"url": "http://invalid-url", "status_code": None, "is_reachable": False, "error": "Invalid URL format"},
    ]
    # Write results to the JSON file
    with open(output_file, "w") as f:
        json.dump(results, f, indent=4)

    # Verify the file contents
    with open(output_file, "r") as f:
        saved_results = json.load(f)
        assert saved_results == results
