import json
import logging
import os
from typing import Optional, Tuple
from urllib.parse import urlparse
from firecrawl import FirecrawlApp
from app.utils.validators import validate_url

# ------------------------------------------------------
# Configure logging
# ------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# Initialize FirecrawlApp with API key
app = FirecrawlApp(api_key="fc-f9d14b7260664d109ca9c9fad1a31360")

# ------------------------------------------------------
# 1. Scrape the site with Firecrawl
# ------------------------------------------------------
def crawl_website(url: str, page_limit: int = 3, output_dir: Optional[str] = None) -> Tuple[str, str]:
    """
    Crawl a website using Firecrawl and save the results to JSON files.
    
    Args:
        url (str): The URL of the website to crawl
        page_limit (int, optional): Maximum number of pages to crawl. Defaults to 3.
        output_dir (Optional[str], optional): Directory to save output files. Defaults to None.
    
    Returns:
        Tuple[str, str]: (scraped_filename, deduplicated_filename) - Paths to the generated files
    """
    # Extract domain from URL for filename
    domain = urlparse(url).netloc
    # Remove www. prefix if present
    if domain.startswith('www.'):
        domain = domain[4:]
    # Replace dots with underscores for filename
    domain_filename = domain.replace('.', '_')
    
    # Set output directory - use current directory if none specified
    if output_dir:
        base_path = output_dir
    else:
        base_path = os.getcwd()
    
    # Define filenames with absolute paths
    scraped_filename = os.path.join(base_path, f"{domain_filename}_scraped_data.json")
    deduplicated_filename = os.path.join(base_path, f"{domain_filename}_deduplicated_data.json")
    
    logging.info(f"Initializing crawl for '{url}' with limit={page_limit} pages.")
    try:
        crawl_status = app.crawl_url(
            url,
            params={
                'limit': page_limit,
                'scrapeOptions': {'formats': ['markdown']}
            },
            poll_interval=30
        )
        logging.info("Crawl completed successfully.")
        
        # Process the crawled data
        data = crawl_status.get('data', [])
        deduped_data, duplicates_list = deduplicate_in_memory(data)
        
        # Remove array duplicates
        deduped_data_no_array_dupes = remove_array_duplicates(deduped_data)
        duplicates_no_array_dupes = remove_array_duplicates(duplicates_list)
        
        # Write results to files, ensuring we overwrite any existing files
        logging.info(f"Writing unique data to '{scraped_filename}'.")
        try:
            # Ensure the directory exists
            os.makedirs(os.path.dirname(scraped_filename), exist_ok=True)
            with open(scraped_filename, "w", encoding="utf-8") as f_out:
                json.dump(deduped_data_no_array_dupes, f_out, indent=4)
            logging.info(f"Wrote unique data to '{scraped_filename}'.")
        except Exception as e:
            logging.error(f"Failed to write data to '{scraped_filename}': {e}")
            raise
        
        logging.info(f"Writing deduplication results to '{deduplicated_filename}'.")
        try:
            # Ensure the directory exists
            os.makedirs(os.path.dirname(deduplicated_filename), exist_ok=True)
            # Build a structure with data and duplicates
            output_data = {
                "data": deduped_data_no_array_dupes,
                "duplicates": duplicates_no_array_dupes
            }
            
            with open(deduplicated_filename, "w", encoding="utf-8") as f_out:
                json.dump(output_data, f_out, indent=4)
            logging.info(f"Wrote deduplication results to '{deduplicated_filename}' successfully.")
        except Exception as e:
            logging.error(f"Failed to write deduplication data to '{deduplicated_filename}': {e}")
            raise
        
        return scraped_filename, deduplicated_filename
        
    except Exception as e:
        logging.error(f"Crawl failed with an exception: {e}")
        raise

def gather_scraped_content(url: Optional[str] = None, max_pages: Optional[int] = 3, force_crawl: bool = False) -> str:
    """
    Loads the scraped website content and returns a single string containing the content of the pages.
    
    Args:
        url (Optional[str], optional): URL to crawl if provided. Defaults to None.
        max_pages (Optional[int], optional): Maximum number of pages to process. Defaults to 3.
        force_crawl (bool, optional): Force a new crawl even if data exists. Defaults to False.
    
    Returns:
        str: Joined text content from all scraped pages
        
    Raises:
        ValueError: If the URL is invalid or no pages are found to process
        RuntimeError: If there's an error during crawling
    """
    # Default filename for when no URL is provided
    filename = "scraped_data.json"
    
    # If URL is provided, validate and process it
    if url:
        # Validate URL
        if not validate_url(url):
            raise ValueError(f"Invalid URL format: {url}")
        
        # Determine filename based on the domain
        domain = urlparse(url).netloc
        if domain.startswith('www.'):
            domain = domain[4:]
        domain_filename = domain.replace('.', '_')
        filename = f"{domain_filename}_scraped_data.json"
        
        # Log the current state
        logging.info(f"Processing URL: {url}")
        logging.info(f"Force crawl flag: {force_crawl}")
        logging.info(f"Target file: {filename}")
        logging.info(f"File exists: {os.path.exists(filename)}")
        
        # Determine if we should crawl
        should_crawl = force_crawl or not os.path.exists(filename)
        logging.info(f"Should crawl: {should_crawl}")
            
        if should_crawl:
            logging.info(f"Starting crawl for: {url}")
            try:
                # Crawl the website and save to file
                crawl_website(url, page_limit=max_pages if max_pages is not None else 3)
                logging.info(f"Successfully crawled website and saved to {filename}")
            except Exception as e:
                logging.error(f"Failed to crawl website: {str(e)}")
                raise RuntimeError(f"Failed to crawl website {url}: {str(e)}")
        else:
            logging.info(f"Using cached data from {filename}")
    
    # Try to load the content from the file
    try:
        logging.info(f"Reading content from {filename}")
        with open(filename, "r", encoding="utf-8") as f:
            data = json.load(f)
            
        # Extract text content from the data
        pages = []
        if isinstance(data, list):
            for entry in data:
                if isinstance(entry, dict) and "markdown" in entry:
                    pages.append(entry["markdown"])
        elif isinstance(data, dict) and "data" in data:
            for entry in data["data"]:
                if isinstance(entry, dict) and "markdown" in entry:
                    pages.append(entry["markdown"])
                    
        if not pages:
            raise ValueError(f"No valid content found in {filename}")
            
        logging.info(f"Successfully extracted {len(pages)} pages of content")
        return "\n\n".join(pages)
        
    except FileNotFoundError:
        raise ValueError(f"File not found: {filename}")
    except json.JSONDecodeError:
        raise ValueError(f"Invalid JSON format in {filename}")
    except Exception as e:
        raise RuntimeError(f"Error processing file {filename}: {str(e)}")

# ------------------------------------------------------
# 2. Deduplicate by 'id'
#    Returns (deduped_data, duplicates_list).
# ------------------------------------------------------
def deduplicate_in_memory(data):
    """
    Given JSON-like data (list or dict with 'data'), deduplicate by 'id'.
    - deduped_data: Each 'id' appears only once.
    - duplicates_list: Any extra records sharing the same 'id'.
    """
    unique_dict = {}
    duplicates_list = []

    # CASE A: data is a list of objects
    if isinstance(data, list):
        for entry in data:
            if "id" in entry:
                # If this 'id' was seen before, it's a duplicate
                if entry["id"] in unique_dict:
                    duplicates_list.append(entry)
                else:
                    unique_dict[entry["id"]] = entry
            else:
                # If no 'id', we give it a generated key to keep it
                fake_id = f"no_id_{len(unique_dict) + len(duplicates_list)}"
                unique_dict[fake_id] = entry
    
    # CASE B: data is a dict with a 'data' array
    elif isinstance(data, dict) and "data" in data and isinstance(data["data"], list):
        for entry in data["data"]:
            if "id" in entry:
                if entry["id"] in unique_dict:
                    duplicates_list.append(entry)
                else:
                    unique_dict[entry["id"]] = entry
            else:
                fake_id = f"no_id_{len(unique_dict) + len(duplicates_list)}"
                unique_dict[fake_id] = entry
    
    # Convert the dict of unique entries back to a list
    deduped_data = list(unique_dict.values())
    
    return deduped_data, duplicates_list

# ------------------------------------------------------
# 3. Remove duplicates from arrays within objects
# ------------------------------------------------------
def remove_array_duplicates(data_list):
    """
    For each object in the list, find any arrays and deduplicate them.
    """
    result = []
    
    for item in data_list:
        # Create a copy of the item to modify
        new_item = {}
        
        for key, value in item.items():
            # If this is an array, deduplicate it
            if isinstance(value, list):
                # For simple types (strings, numbers), we can use set()
                if all(isinstance(x, (str, int, float, bool)) for x in value):
                    new_item[key] = list(set(value))
                else:
                    # For complex types, we'd need a more sophisticated approach
                    # For now, just keep the original
                    new_item[key] = value
            else:
                new_item[key] = value
        
        result.append(new_item)
    
    return result

# ------------------------------------------------------
# 7. Load general website content from scraped data file
# ------------------------------------------------------
def load_scraped_website_content(
    filename: str = "scraped_data.json",
    content_key: str = "markdown",
    max_pages: int = None # type: ignore
) -> list:
    """
    A general-purpose function to load text from your scraped data JSON file.
    Returns a list of strings, one per item in the JSON, focusing on the specified `content_key`
    (defaults to 'markdown').

    :param filename: The JSON file to load (defaults to 'scraped_data.json')
    :param content_key: The key in each record containing the text content (e.g. 'markdown')
    :param max_pages: If provided, limits how many records to return
    :return: List of page contents as strings
    """
    try:
        with open(filename, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        logging.error("Could not read or parse '%s': %s", filename, e)
        return []

    # 'data' might be a list or dict.
    # Usually, 'scraped_data.json' is a list of items from Firecrawl.
    pages = []

    if isinstance(data, list):
        for entry in data:
            # Some records might have 'markdown' content
            text = entry.get(content_key, "")
            if isinstance(text, str):
                pages.append(text)
            # If content_key is a list, we might join them or handle differently
    elif isinstance(data, dict) and "data" in data:
        # If it's a dict with a 'data' list inside
        for entry in data["data"]:
            text = entry.get(content_key, "")
            if isinstance(text, str):
                pages.append(text)
    else:
        logging.warning("Unknown structure in '%s'. Returning empty list.", filename)
        return []

    if max_pages is not None:
        pages = pages[:max_pages]

    return pages

# For backward compatibility - crawl the default site if this module is run directly
if __name__ == "__main__":
    default_url = 'https://www.innquest.com/'
    crawl_website(default_url)
    gather_scraped_content(url=default_url)
