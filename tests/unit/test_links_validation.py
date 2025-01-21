import requests
import json
import pytest

# Load links from the JSON file
def load_links(file_path="links.json"):
    with open(file_path, "r") as file:
        data = json.load(file)
        return data.get("links", [])

def validate_url(url):
    """
    Validates a URL and categorizes it based on validity and redirection status.

    Args:
        url (str): The URL to validate.

    Returns:
        dict: A dictionary with the URL, status code, redirection status, and validity.
    """
    try:
        response = requests.head(url, allow_redirects=False, timeout=5)
        is_redirected = 300 <= response.status_code < 400
        is_valid = response.ok or is_redirected
        return {
            "url": url,
            "status_code": response.status_code,
            "is_redirected": is_redirected,
            "is_valid": is_valid,
        }
    except requests.exceptions.RequestException as e:
        return {
            "url": url,
            "status_code": None,
            "is_redirected": False,
            "is_valid": False,
            "error": str(e),
        }

def classify_url(result):
    """
    Classifies the URL based on validation result.

    Args:
        result (dict): Validation result dictionary.

    Returns:
        str: The classification of the URL.
    """
    if result["is_valid"]:
        if result["is_redirected"]:
            return "Valid with redirect"
        return "Valid with no redirect"
    else:
        if result["is_redirected"]:
            return "Not valid with redirect"
        return "Not valid with no redirect"

@pytest.fixture
def load_links_fixture():
    """Fixture to load links from the JSON file."""
    return load_links()

def test_urls(load_links_fixture):
    """Test all URLs in the JSON file and classify them."""
    links = load_links_fixture
    results = []

    for url in links:
        result = validate_url(url)
        classification = classify_url(result)
        results.append({"url": url, "classification": classification, "details": result})

        # Print the classification
        print(f"URL: {url} -> {classification}")

    # Assertions for the test cases (example: ensure at least one valid URL exists)
    assert any(res["classification"] == "Valid with no redirect" for res in results), "No valid URLs without redirect found."
    assert any(res["classification"] == "Valid with redirect" for res in results), "No valid URLs with redirect found."
    assert any(res["classification"] == "Not valid with no redirect" for res in results), "All URLs are valid, which is unexpected."

def test_save_results_to_json(tmp_path, load_links_fixture):
    """Test saving classification results to a JSON file."""
    output_file = tmp_path / "results.json"
    links = load_links_fixture
    results = []

    for url in links:
        result = validate_url(url)
        classification = classify_url(result)
        results.append({"url": url, "classification": classification, "details": result})

    # Write results to the JSON file
    with open(output_file, "w") as f:
        json.dump(results, f, indent=4)

    # Verify the file contents
    with open(output_file, "r") as f:
        saved_results = json.load(f)
        assert saved_results == results
