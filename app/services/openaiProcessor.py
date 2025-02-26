from openai import AzureOpenAI
import json
import os
import argparse
import re
import time
from typing import Optional, Dict, Any
from urllib.parse import urlparse
from pydantic import ValidationError
from app.models.reportsModels import HighLevelBusinessWebsiteScrapeReport
from app.utils.firecrawlApp import load_scraped_website_content, crawl_website
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Initialize Azure OpenAI client with the correct Azure settings
client = AzureOpenAI(
    api_key="c15e05017b07470f86d6192aa2755d37",
    api_version="2024-08-01-preview",
    azure_endpoint="https://valstone-prod-openai.openai.azure.com"
)

# Define the JSON schema for structured output
REPORT_SCHEMA = {
    "type": "object",
    "properties": {
        "overview": {
            "type": "object",
            "properties": {
                "company_snapshot": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string"},
                        "headquarters": {"type": "string"},
                        "year_founded": {"type": "string"},
                        "notable_leadership": {"type": "array", "items": {"type": "string"}}
                    }
                },
                "website_summary": {
                    "type": "object",
                    "properties": {
                        "pages_scraped_reviewed": {"type": "array", "items": {"type": "string"}},
                        "key_observations": {"type": "array", "items": {"type": "string"}}
                    }
                }
            }
        },
        "products_and_services": {
            "type": "object",
            "properties": {
                "core_offerings": {
                    "type": "object",
                    "properties": {
                        "primary_products_services": {"type": "array", "items": {"type": "string"}},
                        "key_features_capabilities": {"type": "array", "items": {"type": "string"}},
                        "target_use_cases": {"type": "array", "items": {"type": "string"}}
                    }
                },
                "additional_solutions": {
                    "type": "object",
                    "properties": {
                        "secondary_products": {"type": "array", "items": {"type": "string"}},
                        "integrations": {"type": "array", "items": {"type": "string"}}
                    }
                }
            }
        },
        "market_and_audience": {
            "type": "object",
            "properties": {
                "target_audience": {
                    "type": "object",
                    "properties": {
                        "customer_segments": {"type": "array", "items": {"type": "string"}},
                        "customer_pain_points": {"type": "array", "items": {"type": "string"}}
                    }
                },
                "competitive_landscape": {
                    "type": "object",
                    "properties": {
                        "direct_competitors": {"type": "array", "items": {"type": "string"}},
                        "differentiators": {"type": "array", "items": {"type": "string"}}
                    }
                }
            }
        },
        "business_model_and_pricing": {
            "type": "object",
            "properties": {
                "revenue_model": {
                    "type": "object",
                    "properties": {
                        "model_type": {"type": "string"},
                        "pricing_tiers": {"type": "array", "items": {"type": "string"}}
                    }
                },
                "key_partnerships": {
                    "type": "object",
                    "properties": {
                        "partners_distributors": {"type": "array", "items": {"type": "string"}},
                        "promotional_offers": {"type": "array", "items": {"type": "string"}}
                    }
                }
            }
        },
        "team_and_culture": {
            "type": "object",
            "properties": {
                "company_culture": {
                    "type": "object",
                    "properties": {
                        "mission_values": {"type": "array", "items": {"type": "string"}},
                        "employee_spotlight": {"type": "array", "items": {"type": "string"}}
                    }
                },
                "growth_recruitment": {
                    "type": "object",
                    "properties": {
                        "career_opportunities": {"type": "array", "items": {"type": "string"}},
                        "industry_expertise": {"type": "array", "items": {"type": "string"}}
                    }
                }
            }
        },
        "high_level_observations_and_conclusion": {
            "type": "object",
            "properties": {
                "overall_positioning": {"type": "string"},
                "potential_strengths": {"type": "array", "items": {"type": "string"}},
                "potential_gaps_limitations": {"type": "array", "items": {"type": "string"}}
            }
        }
    }
}

# Keep the old structure hint for reference in prompts
STRUCTURE_HINT = """
{
  "overview": {
    "company_snapshot": {
      "name": "",
      "headquarters": "",
      "year_founded": "",
      "notable_leadership": []
    },
    "website_summary": {
      "pages_scraped_reviewed": [],
      "key_observations": []
    }
  },
  "products_and_services": {
    "core_offerings": {
      "primary_products_services": [],
      "key_features_capabilities": [],
      "target_use_cases": []
    },
    "additional_solutions": {
      "secondary_products": [],
      "integrations": []
    }
  },
  "market_and_audience": {
    "target_audience": {
      "customer_segments": [],
      "customer_pain_points": []
    },
    "competitive_landscape": {
      "direct_competitors": [],
      "differentiators": []
    }
  },
  "business_model_and_pricing": {
    "revenue_model": {
      "model_type": "",
      "pricing_tiers": []
    },
    "key_partnerships": {
      "partners_distributors": [],
      "promotional_offers": []
    }
  },
  "team_and_culture": {
    "company_culture": {
      "mission_values": [],
      "employee_spotlight": []
    },
    "growth_recruitment": {
      "career_opportunities": [],
      "industry_expertise": []
    }
  },
  "high_level_observations_and_conclusion": {
    "overall_positioning": "",
    "potential_strengths": [],
    "potential_gaps_limitations": []
  }
}
"""

def validate_url(url: str) -> bool:
    """
    Validates if the provided string is a valid URL.
    
    Args:
        url (str): The URL to validate
        
    Returns:
        bool: True if the URL is valid, False otherwise
    """
    # Basic URL validation using regex
    url_pattern = re.compile(
        r'^(https?://)'  # http:// or https://
        r'([a-zA-Z0-9]([a-zA-Z0-9-]*[a-zA-Z0-9])?\.)+' # domain
        r'[a-zA-Z0-9]([a-zA-Z0-9-]*[a-zA-Z0-9])?' # domain suffix
        r'(/[a-zA-Z0-9._~:/?#[\]@!$&\'()*+,;=]*)?' # path
        r'$'
    )
    
    # Check if the URL matches the pattern
    if not url_pattern.match(url):
        return False
    
    # Parse the URL to check if it has a valid scheme and netloc
    parsed_url = urlparse(url)
    if not all([parsed_url.scheme, parsed_url.netloc]):
        return False
    
    return True

def gather_scraped_content(url: Optional[str] = None, max_pages: int = None, force_crawl: bool = False) -> str: # type: ignore
    """
    Loads the scraped website content and returns a single string containing the content of the pages.
    
    Args:
        url (Optional[str], optional): URL to crawl if provided. Defaults to None.
        max_pages (int, optional): Maximum number of pages to process. Defaults to None.
        force_crawl (bool, optional): Force a new crawl even if data exists. Defaults to False.
    
    Returns:
        str: Joined text content from all scraped pages
        
    Raises:
        ValueError: If the URL is invalid or no pages are found to process
        RuntimeError: If there's an error during crawling
    """
    filename = "scraped_data.json"  # Default filename
    
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
        
        # Check if we need to crawl the website
        if force_crawl or not os.path.exists(filename):
            print(f"Crawling website: {url}")
            try:
                scraped_filename, _ = crawl_website(url, page_limit=max_pages or 3)
                filename = scraped_filename
            except Exception as e:
                raise RuntimeError(f"Failed to crawl website {url}: {str(e)}")
    
    # Load the content from the file
    try:
        pages_content = load_scraped_website_content(filename=filename, max_pages=max_pages)
        if not pages_content:
            raise ValueError(f"No pages found to process in {filename}.")
        
        joined_text = "\n\n---PAGE BREAK---\n\n".join(pages_content)
        return joined_text
    except FileNotFoundError:
        raise ValueError(f"File not found: {filename}. Please make sure the website has been crawled.")
    except Exception as e:
        raise RuntimeError(f"Error loading content from {filename}: {str(e)}")

def build_report_prompt(pages_text: str) -> str:
    """
    Constructs the prompt for OpenAI with the scraped page content.
    
    Args:
        pages_text (str): The scraped page content
        
    Returns:
        str: The prompt for OpenAI
    """
    prompt = f"""
I have scraped some pages from a company's website. 
Below is the text. Please read it carefully and extract information to create a comprehensive business report.

--SCRAPED PAGE CONTENT--
{pages_text}

Based on this content, create a detailed business report in JSON format that covers the company's overview, products/services, 
target market, business model, team/culture, and high-level observations.

Please structure your JSON response EXACTLY according to the following schema:
{STRUCTURE_HINT}

IMPORTANT:
1. Follow the exact structure shown above
2. All fields must be present in your JSON response
3. If information is not available, use empty strings for string fields and empty arrays for array fields
4. Ensure all JSON is properly formatted with correct quotes, commas, and brackets
"""
    return prompt

def send_prompt_to_openai(prompt: str, max_retries: int = 3, retry_delay: int = 5) -> Dict[str, Any]:
    """
    Sends the prompt to Azure OpenAI and returns the structured JSON output.
    
    Args:
        prompt (str): The prompt to send to OpenAI
        max_retries (int, optional): Maximum number of retry attempts. Defaults to 3.
        retry_delay (int, optional): Delay between retries in seconds. Defaults to 5.
    
    Returns:
        Dict[str, Any]: The structured JSON output from OpenAI
        
    Raises:
        RuntimeError: If all retry attempts fail
    """
    attempt = 0
    last_error = None
    
    system_message = """
You are a helpful assistant that analyzes website content and extracts business information.
Output your response as a JSON object that EXACTLY follows the structure provided by the user.
Do not deviate from the structure. If information is not available, use empty strings for string fields and empty arrays for array fields.
Do not add any explanatory text before or after the JSON.
"""
    
    while attempt < max_retries:
        try:
            print(f"Sending request to OpenAI (attempt {attempt + 1}/{max_retries})...")
            
            response = client.chat.completions.create(
                model="gpt-4o",  # Use the correct deployment name
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"},
                temperature=0,
            )
            
            raw_json_output = response.choices[0].message.content
            
            # Validate that we got a non-empty response
            if not raw_json_output or not raw_json_output.strip():
                raise ValueError("OpenAI returned an empty response")
            
            # Parse the JSON response
            try:
                data_dict: Dict[str, Any] = json.loads(raw_json_output)
                print("Successfully received and parsed JSON response from OpenAI")
                
                # Print the structure of the received JSON for debugging
                print("JSON structure received:")
                for key in data_dict:
                    print(f"- {key}")
                    if isinstance(data_dict[key], dict):
                        for subkey in data_dict[key]:
                            print(f"  - {subkey}")
                
                return data_dict
            except json.JSONDecodeError as e:
                print(f"JSON parsing error: {str(e)}")
                print(f"First 100 chars of response: {raw_json_output[:100]}...")
                raise ValueError(f"Failed to parse JSON response: {str(e)}")
            
        except Exception as e:
            last_error = e
            attempt += 1
            print(f"Attempt {attempt}/{max_retries} failed: {str(e)}")
            
            if attempt < max_retries:
                print(f"Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
    
    # If we've exhausted all retries, raise the last error
    raise RuntimeError(f"Azure OpenAI API Error after {max_retries} attempts: {str(last_error)}")

def parse_into_pydantic(data_dict: Dict[str, Any]) -> HighLevelBusinessWebsiteScrapeReport:
    """
    Parses the dictionary into a HighLevelBusinessWebsiteScrapeReport model.
    
    Args:
        data_dict (Dict[str, Any]): The dictionary to parse
        
    Returns:
        HighLevelBusinessWebsiteScrapeReport: The parsed Pydantic model
        
    Raises:
        ValueError: If the dictionary doesn't match the Pydantic model
    """
    try:
        report_model = HighLevelBusinessWebsiteScrapeReport(**data_dict)
        return report_model
    except ValidationError as e:
        raise ValueError(f"JSON does not match the Pydantic model: {e}")

def save_report_to_json(report_model: HighLevelBusinessWebsiteScrapeReport, filename: Optional[str] = None):
    """
    Saves the report model into a JSON file.
    
    Args:
        report_model (HighLevelBusinessWebsiteScrapeReport): The report model to save
        filename (Optional[str], optional): Custom filename. If None, a default name will be used.
        
    Raises:
        RuntimeError: If there's an error during file saving
    """
    if not filename:
        filename = "final_website_report.json"
    
    try:
        # Ensure the directory exists
        directory = os.path.dirname(filename)
        if directory and not os.path.exists(directory):
            os.makedirs(directory)
            
        # Use model_dump_json instead of json for Pydantic v2 compatibility
        with open(filename, "w", encoding="utf-8") as f:
            try:
                # Try the new Pydantic v2 method first
                json_data = report_model.model_dump_json(indent=4)
            except AttributeError:
                # Fall back to the old method for Pydantic v1
                json_data = report_model.json(indent=4)
            
            f.write(json_data)
        print(f"✅ Report saved as {filename}")
    except Exception as e:
        raise RuntimeError(f"Failed to save report: {e}")

def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Process a website and generate a business report")
    parser.add_argument("--url", type=str, help="URL of the website to crawl and analyze")
    parser.add_argument("--max-pages", type=int, default=3, help="Maximum number of pages to process")
    parser.add_argument("--force-crawl", action="store_true", help="Force a new crawl even if data exists")
    parser.add_argument("--output", type=str, help="Custom output filename for the report")
    parser.add_argument("--retries", type=int, default=3, help="Number of retries for OpenAI API calls")
    args = parser.parse_args()
    
    # Validate URL if provided
    if args.url and not validate_url(args.url):
        print(f"Error: Invalid URL format: {args.url}")
        return
    
    # Step 1: Gather scraped content
    try:
        print("Gathering scraped content...")
        pages_text = gather_scraped_content(
            url=args.url, 
            max_pages=args.max_pages,
            force_crawl=args.force_crawl
        )
    except ValueError as e:
        print(f"Error: {e}")
        return
    except RuntimeError as e:
        print(f"Error during content gathering: {e}")
        return
    except Exception as e:
        print(f"Unexpected error during content gathering: {e}")
        return

    # Step 2: Build the prompt
    prompt = build_report_prompt(pages_text)
    
    # Step 3: Send prompt to Azure OpenAI with structured output
    try:
        print("Sending prompt to Azure OpenAI...")
        data_dict = send_prompt_to_openai(prompt, max_retries=args.retries)
        print("Structured JSON output received.")
    except RuntimeError as e:
        print(f"Error during OpenAI call: {e}")
        return
    except Exception as e:
        print(f"Unexpected error during OpenAI call: {e}")
        return

    # Step 4: Parse the JSON into the Pydantic model
    try:
        print("Parsing JSON into Pydantic model...")
        report_model = parse_into_pydantic(data_dict)
        print("JSON parsed successfully.")
    except ValueError as e:
        print(f"Error during JSON parsing: {e}")
        return
    except Exception as e:
        print(f"Unexpected error during JSON parsing: {e}")
        return

    # Step 5: Save the report to a JSON file
    try:
        print("Saving report to JSON file...")
        # Generate a custom filename based on the URL if provided
        custom_filename = args.output
        if args.url and not custom_filename:
            domain = urlparse(args.url).netloc
            if domain.startswith('www.'):
                domain = domain[4:]
            domain_filename = domain.replace('.', '_')
            custom_filename = f"{domain_filename}_report.json"
        
        save_report_to_json(report_model, filename=custom_filename)
    except RuntimeError as e:
        print(f"Error during file saving: {e}")
        return
    except Exception as e:
        print(f"Unexpected error during file saving: {e}")
        return

    print("Process completed successfully!")

if __name__ == '__main__':
    main()
