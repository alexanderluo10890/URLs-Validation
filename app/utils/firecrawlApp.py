import json
from firecrawl import FirecrawlApp

# -------------------------------
# 1. Scrape the site with Firecrawl
# -------------------------------
app = FirecrawlApp(api_key="fc-aaa191b98dc94ab8b9f06f304fa89ab2")

# Crawl google.com, limit to 3 pages, ensure JSON format
crawl_status = app.crawl_url(
    'google.com',
    params={
        'limit': 3,
        'scrapeOptions': {'formats': ['markdown', 'html']}
    },
    poll_interval=30
)

# Save scraped data to a JSON file
json_filename = "scraped_data.json"
with open(json_filename, "w", encoding="utf-8") as json_file:
    json.dump(crawl_status, json_file, indent=4)

print(f"Scraped data saved to {json_filename}")

# -------------------------------
# 2. Deduplicate the data
# -------------------------------
def deduplicate_json_data(input_file, output_file):
    """
    Load JSON data from 'input_file', remove duplicates by 'id',
    then save to 'output_file'.
    """

    with open(input_file, "r", encoding="utf-8") as f:
        # Assuming 'crawl_status' is either a list of items or
        # a dict that contains a list under some key.
        data = json.load(f)

    # Prepare a dict to collect unique entries by 'id'
    unique_dict = {}

    # CASE A: If the JSON is an array of objects
    if isinstance(data, list):
        for entry in data:
            # Use 'id' as a key for dedup
            # If there's no 'id', you might need another unique field
            if "id" in entry:
                unique_dict[entry["id"]] = entry

        # After collecting, convert the dict back to a list
        deduplicated_data = list(unique_dict.values())
        
        # Write deduplicated data
        with open(output_file, "w", encoding="utf-8") as f_out:
            json.dump(deduplicated_data, f_out, indent=4)
    
    # CASE B: If the JSON is a dict containing a list under "data" or "results"
    # (Customize this part if your data structure is different.)
    elif isinstance(data, dict) and "data" in data and isinstance(data["data"], list):
        for entry in data["data"]:
            if "id" in entry:
                unique_dict[entry["id"]] = entry

        # Replace with deduplicated
        data["data"] = list(unique_dict.values())
        
        with open(output_file, "w", encoding="utf-8") as f_out:
            json.dump(data, f_out, indent=4)
    
    else:
        # If the structure is neither a list nor a known dict pattern,
        # just write it back or handle as needed
        with open(output_file, "w", encoding="utf-8") as f_out:
            json.dump(data, f_out, indent=4)

    print(f"Deduplicated data saved to {output_file}")

# Actually run the dedup
deduplicate_json_data(json_filename, "deduplicated_data.json")
