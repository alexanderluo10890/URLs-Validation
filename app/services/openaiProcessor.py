from openai import AzureOpenAI
import json
import os
from pydantic import ValidationError
from app.models.reportsModels import HighLevelBusinessWebsiteScrapeReport
from app.utils.firecrawlApp import load_scraped_website_content
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Initialize Azure OpenAI client with your Azure settings
client = AzureOpenAI(
    api_key="6c0b26151fc04cadae38b20ad67ab241",
    api_version="2024-11-20",
    azure_endpoint="https://vals-prod-openai.openai.azure.com"
)

# JSON structure hint for the report format
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

def gather_scraped_content(max_pages: int = None) -> str: # type: ignore
    """
    Loads the scraped website content from 'scraped_data.json' and returns a 
    single string containing the content of the pages.
    """
    pages_content = load_scraped_website_content(max_pages=max_pages)
    if not pages_content:
        raise ValueError("No pages found to process.")
    joined_text = "\n\n---PAGE BREAK---\n\n".join(pages_content)
    return joined_text

def build_report_prompt(pages_text: str) -> tuple:
    """
    Constructs the prompt for OpenAI by combining a system instruction, 
    the JSON structure hint, and the scraped page content.
    Returns a tuple: (system_prompt, user_prompt)
    """
    system_prompt = "You are a helpful assistant that outputs valid JSON only."
    user_prompt = f"""
I have scraped some pages from a company's website. 
Below is the text. Please read it carefully, then produce a **valid JSON** 
that matches the following structure:
{STRUCTURE_HINT}

Fill in the relevant fields with the data you find. If unknown, leave them empty.

--SCRAPED PAGE CONTENT--
{pages_text}

Remember:
1) Return **ONLY valid JSON**. No markdown or extra commentary.
2) Ensure the JSON keys **exactly match the structure above**.
"""
    return system_prompt, user_prompt

def send_prompt_to_openai(prompt: str) -> str:
    """
    Sends the prompt to Azure OpenAI and returns the raw JSON output.
    """
    try:
        response = client.chat.completions.create(
            model="gpt-4o",  # Use your actual Azure deployment name here
            messages=[
                {"role": "system", "content": "You are a helpful assistant that outputs valid JSON only."},
                {"role": "user", "content": prompt}
            ],
            temperature=0,
        )
        raw_json_output = response.choices[0].message.content
        return raw_json_output # type: ignore
    except Exception as e:
        raise RuntimeError(f"Azure OpenAI API Error: {str(e)}")

def parse_into_pydantic(raw_json_output: str) -> HighLevelBusinessWebsiteScrapeReport:
    """
    Parses the raw JSON output into a HighLevelBusinessWebsiteScrapeReport model.
    """
    try:
        data_dict = json.loads(raw_json_output)
    except json.JSONDecodeError as e:
        raise ValueError(f"OpenAI returned invalid JSON: {e}")
    
    try:
        report_model = HighLevelBusinessWebsiteScrapeReport(**data_dict)
        return report_model
    except ValidationError as e:
        raise ValueError(f"JSON does not match the Pydantic model: {e}")

def save_report_to_json(report_model: HighLevelBusinessWebsiteScrapeReport, filename: str = "final_website_report.json"):
    """
    Saves the report model into a JSON file.
    """
    try:
        with open(filename, "w", encoding="utf-8") as f:
            f.write(report_model.json(indent=4))
        print(f"✅ Report saved as {filename}")
    except Exception as e:
        raise RuntimeError(f"Failed to save report: {e}")

def main():
    # Step 1: Gather scraped content
    try:
        print("Gathering scraped content...")
        pages_text = gather_scraped_content(max_pages=3)
    except Exception as e:
        print(f"Error during content gathering: {e}")
        return

    # Step 2: Build the prompt
    system_prompt, user_prompt = build_report_prompt(pages_text)
    
    # Step 3: Send prompt to Azure OpenAI
    try:
        print("Sending prompt to Azure OpenAI...")
        raw_json = send_prompt_to_openai(user_prompt)
        print("Raw JSON output received.")
    except Exception as e:
        print(f"Error during OpenAI call: {e}")
        return

    # Step 4: Parse the JSON into the Pydantic model
    try:
        print("Parsing JSON into Pydantic model...")
        report_model = parse_into_pydantic(raw_json)
        print("JSON parsed successfully.")
    except Exception as e:
        print(f"Error during JSON parsing: {e}")
        return

    # Step 5: Save the report to a JSON file
    try:
        print("Saving report to JSON file...")
        save_report_to_json(report_model)
    except Exception as e:
        print(f"Error during file saving: {e}")
        return

    print("Process completed successfully!")

if __name__ == '__main__':
    main()
