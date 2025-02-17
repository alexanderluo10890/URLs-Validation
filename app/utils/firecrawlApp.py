import json
import logging
from firecrawl import FirecrawlApp

# ------------------------------------------------------
# Configure logging
# ------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# ------------------------------------------------------
# 1. Scrape the site with Firecrawl
# ------------------------------------------------------
logging.info("Initializing Firecrawl app...")
app = FirecrawlApp(api_key="fc-aaa191b98dc94ab8b9f06f304fa89ab2")

logging.info("Starting crawl for 'https://www.innquest.com/' with limit=3 pages.")
try:
    crawl_status = app.crawl_url(
        'https://www.innquest.com/',
        params={
            'limit': 3,
            'scrapeOptions': {'formats': ['markdown']}
        },
        poll_interval=30
    )
    logging.info("Crawl completed successfully.")
except Exception as e:
    logging.error("Crawl failed with an exception: %s", e)
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

        return list(unique_dict.values()), duplicates_list

    # CASE B: data is a dict containing a list under data["data"]
    elif isinstance(data, dict) and "data" in data and isinstance(data["data"], list):
        new_data_list = []
        for entry in data["data"]:
            if "id" in entry:
                if entry["id"] in unique_dict:
                    duplicates_list.append(entry)
                else:
                    unique_dict[entry["id"]] = entry
                    new_data_list.append(entry)
            else:
                fake_id = f"no_id_{len(unique_dict) + len(duplicates_list)}"
                unique_dict[fake_id] = entry
                new_data_list.append(entry)

        deduped_data = dict(data)
        deduped_data["data"] = new_data_list
        return deduped_data, duplicates_list

    # If unknown format, return data as-is (no duplicates recognized)
    return data, []

# ------------------------------------------------------
# 3. Remove repeated elements from arrays (inside each record)
# ------------------------------------------------------
def remove_array_duplicates(obj):
    """
    Recursively walk 'obj'.
    Whenever we find a list, remove repeated items 
    (keeping the first occurrence). This preserves the order.
    """
    if isinstance(obj, dict):
        for k, v in obj.items():
            obj[k] = remove_array_duplicates(v)
        return obj

    elif isinstance(obj, list):
        seen = set()
        new_list = []
        for item in obj:
            if isinstance(item, (dict, list)):
                # Convert sub-structure to a string so we can track if we've seen it
                item_key = json.dumps(item, sort_keys=True)
            else:
                item_key = item

            if item_key not in seen:
                seen.add(item_key)
                new_list.append(remove_array_duplicates(item))
            # else: it's a duplicate array element, skip it
        return new_list

    else:
        return obj

# ------------------------------------------------------
# 4. Perform the ID-based deduplication
# ------------------------------------------------------
logging.info("Starting in-memory deduplication by 'id'...")
deduped_data, duplicates_list = deduplicate_in_memory(crawl_status)

# ------------------------------------------------------
# 5. Remove repeated strings within arrays in both unique + duplicates
# ------------------------------------------------------
logging.info("Removing repeated elements from arrays in 'deduped_data' and 'duplicates_list'...")
deduped_data_no_array_dupes = remove_array_duplicates(deduped_data)
duplicates_no_array_dupes = remove_array_duplicates(duplicates_list)

# ------------------------------------------------------
# 6. Write results:
#    - scraped_data.json => Only the unique data
#    - deduplicated_data.json => Single JSON with { "data": [...], "duplicates": [...] }
# ------------------------------------------------------
scraped_filename = "scraped_data.json"
logging.info("Writing unique data to '%s'.", scraped_filename)
try:
    with open(scraped_filename, "w", encoding="utf-8") as f_out:
        json.dump(deduped_data_no_array_dupes, f_out, indent=4)
    logging.info("Wrote unique data to '%s'.", scraped_filename)
except Exception as e:
    logging.error("Failed to write data to '%s': %s", scraped_filename, e)
    raise

deduplicated_filename = "deduplicated_data.json"
logging.info("Writing deduplication results to '%s'.", deduplicated_filename)
try:
    # Build a structure just like your screenshot:
    # {
    #   "data": [...],       <-- the unique data
    #   "duplicates": [...]
    # }
    output_data = {
        "data": deduped_data_no_array_dupes,
        "duplicates": duplicates_no_array_dupes
    }

    with open(deduplicated_filename, "w", encoding="utf-8") as f_out:
        json.dump(output_data, f_out, indent=4)
    logging.info("Wrote deduplication results to '%s' successfully.", deduplicated_filename)
except Exception as e:
    logging.error("Failed to write deduplication data to '%s': %s", deduplicated_filename, e)
    raise

logging.info("All steps completed successfully.")
