import json
import logging
import os
from typing import Optional, Tuple
from urllib.parse import urlparse
from firecrawl import FirecrawlApp

# ------------------------------------------------------
# Configure logging
# ------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# Initialize FirecrawlApp with API key
app = FirecrawlApp(api_key="fc-aaa191b98dc94ab8b9f06f304fa89ab2")

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
    
    # Set output directory
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
        base_path = output_dir
    else:
        base_path = ""
    
    # Define filenames
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
        
        # Write results to files
        logging.info(f"Writing unique data to '{scraped_filename}'.")
        try:
            with open(scraped_filename, "w", encoding="utf-8") as f_out:
                json.dump(deduped_data_no_array_dupes, f_out, indent=4)
            logging.info(f"Wrote unique data to '{scraped_filename}'.")
        except Exception as e:
            logging.error(f"Failed to write data to '{scraped_filename}': {e}")
            raise
        
        logging.info(f"Writing deduplication results to '{deduplicated_filename}'.")
        try:
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
