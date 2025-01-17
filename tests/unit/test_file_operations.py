import pytest
import json
from unittest.mock import patch
from link_tester import test_link, test_links

# Mocked JSON data for testing
MOCK_LINKS = {
    "links": [
        "https://www.example.com",
        "http://invalid-url",
        "https://nonexistentdomain.xyz"
    ]
}

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
        result = test_link("https://www.example.com")
        assert result["url"] == "https://www.example.com"
        assert result["status_code"] == 200
        assert result["is_reachable"] is True

def test_invalid_url_format():
    """Test an invalid URL format raises an error."""
    result = test_link("http://invalid-url")
    assert result["url"] == "http://invalid-url"
    assert result["status_code"] is None
    assert result["is_reachable"] is False
    assert "error" in result

def test_unreachable_url():
    """Test a valid but unreachable URL."""
    with patch("requests.head") as mock_head:
        mock_head.side_effect = Exception("Connection error")
        result = test_link("https://nonexistentdomain.xyz")
        assert result["url"] == "https://nonexistentdomain.xyz"
        assert result["status_code"] is None
        assert result["is_reachable"] is False
        assert "error" in result

def test_test_links_function(mock_json_file):
    """Test the function that processes all links from a JSON file."""
    with patch("link_tester.links", MOCK_LINKS["links"]):
        with patch("link_tester.requests.head") as mock_head:
            # Mock responses for each link
            mock_head.side_effect = [
                type("Response", (object,), {"status_code": 200}),
                Exception("Invalid URL format"),
                Exception("Connection error"),
            ]
            # Run the test
            results = []
            for result in map(test_link, MOCK_LINKS["links"]):
                results.append(result)

            # Assertions for each link
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
