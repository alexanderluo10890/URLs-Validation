import json
import logging
import os
import re
from typing import Optional, Tuple
from urllib.parse import urlparse
from firecrawl import FirecrawlApp
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

_firecrawl = FirecrawlApp(api_key=os.getenv('FIRECRAWL_API_KEY', ''))


def crawl_website(url: str, page_limit: int = 3, output_dir: Optional[str] = None) -> Tuple[str, str]:
    base_path = output_dir or os.getcwd()
    scraped_filename = os.path.join(base_path, "scraped_data.json")
    deduplicated_filename = os.path.join(base_path, "deduplicated_data.json")

    logger.info(f"Crawling '{url}' (limit={page_limit})")
    crawl_status = _firecrawl.crawl_url(
        url,
        params={'limit': page_limit, 'scrapeOptions': {'formats': ['markdown']}},
        poll_interval=30
    )

    data = crawl_status.get('data', [])
    deduped, duplicates = deduplicate_in_memory(data)
    deduped = remove_array_duplicates(deduped)
    duplicates = remove_array_duplicates(duplicates)

    os.makedirs(os.path.dirname(scraped_filename), exist_ok=True)
    with open(scraped_filename, "w", encoding="utf-8") as f:
        json.dump(deduped, f, indent=4)

    with open(deduplicated_filename, "w", encoding="utf-8") as f:
        json.dump({"data": deduped, "duplicates": duplicates}, f, indent=4)

    os.remove(scraped_filename)
    logger.info(f"Saved deduplicated data to '{deduplicated_filename}'")
    return deduplicated_filename


def clean_scraped_text(text: str) -> str:
    text = re.sub(r'!\[.*?\]\(.*?\)', '', text)         # remove image markdown
    text = re.sub(r'\[.*?\]\(https?://\S+\)', '', text) # remove hyperlinks
    text = re.sub(r'https?://\S+', '', text)            # remove bare URLs
    # remove lines containing flag emojis (country dropdown entries)
    text = re.sub(r'^.*[\U0001F1E0-\U0001F1FF].*$', '', text, flags=re.MULTILINE)
    text = re.sub(r'\n{3,}', '\n\n', text)              # collapse blank lines
    return text.strip()


def load_scraped_website_content(
    filename: str = "scraped_data.json",
    content_key: str = "markdown",
    max_pages: Optional[int] = None
) -> list:
    try:
        with open(filename, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        logger.error("Could not read '%s': %s", filename, e)
        return []

    if isinstance(data, list):
        entries = data
    elif isinstance(data, dict) and "data" in data:
        entries = data["data"]
    else:
        logger.warning("Unknown structure in '%s'", filename)
        return []

    pages = [clean_scraped_text(entry.get(content_key, "")) for entry in entries if isinstance(entry.get(content_key), str)]
    pages = [p for p in pages if p]
    return pages[:max_pages] if max_pages is not None else pages


def deduplicate_in_memory(data) -> Tuple[list, list]:
    unique_dict = {}
    duplicates = []

    items = data if isinstance(data, list) else data.get("data", []) if isinstance(data, dict) else []
    for entry in items:
        if "id" in entry:
            if entry["id"] in unique_dict:
                duplicates.append(entry)
            else:
                unique_dict[entry["id"]] = entry
        else:
            unique_dict[f"no_id_{len(unique_dict) + len(duplicates)}"] = entry

    return list(unique_dict.values()), duplicates


def remove_array_duplicates(data_list: list) -> list:
    result = []
    for item in data_list:
        new_item = {}
        for key, value in item.items():
            if isinstance(value, list) and all(isinstance(x, (str, int, float, bool)) for x in value):
                new_item[key] = list(set(value))
            else:
                new_item[key] = value
        result.append(new_item)
    return result
