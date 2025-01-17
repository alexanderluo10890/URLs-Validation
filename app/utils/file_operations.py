import json
from typing import List

def load_links(json_file: str) -> List[str]:
    """
    Load links from a JSON file.

    Args:
        json_file (str): Path to the JSON file containing the links.

    Returns:
        List[str]: A list of links extracted from the JSON file.
    """
    try:
        with open(json_file, "r") as file:
            data = json.load(file)
            return data.get("links", [])
    except FileNotFoundError:
        print(f"Error: File '{json_file}' not found.")
        return []
    except json.JSONDecodeError:
        print(f"Error: File '{json_file}' is not a valid JSON file.")
        return []

def save_links(json_file: str, links: List[str]) -> None:
    """
    Save a list of links to a JSON file.

    Args:
        json_file (str): Path to the JSON file where the links will be saved.
        links (List[str]): A list of links to save.
    """
    try:
        with open(json_file, "w") as file:
            json.dump({"links": links}, file, indent=4)
        print(f"Links successfully saved to '{json_file}'.")
    except Exception as e:
        print(f"Error saving links to '{json_file}': {e}")

def filter_links(links: List[str], keyword: str) -> List[str]:
    """
    Filter links containing a specific keyword.

    Args:
        links (List[str]): The list of links to filter.
        keyword (str): The keyword to search for in the links.

    Returns:
        List[str]: A list of links containing the specified keyword.
    """
    return [link for link in links if keyword in link]

# Example usage
if __name__ == "__main__":
    # Path to the JSON file
    input_file = "links.json"
    output_file = "filtered_links.json"

    # Load links from the JSON file
    all_links = load_links(input_file)

    # Print the total number of links
    print(f"Total links loaded: {len(all_links)}")

    # Example: Filter links containing "retail"
    keyword = "retail"
    filtered_links = filter_links(all_links, keyword)
    print(f"Total links containing '{keyword}': {len(filtered_links)}")

    # Save the filtered links to a new JSON file
    save_links(output_file, filtered_links)
