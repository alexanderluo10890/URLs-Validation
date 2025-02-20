from openai import AzureOpenAI
import json
import os
from pydantic import ValidationError
from app.models.reportsModels import HighLevelBusinessWebsiteScrapeReport
from app.utils.firecrawlApp import load_scraped_website_content
from dotenv import load_dotenv

# Load environment variables from .env file
client = AzureOpenAI(
    api_key="6c0b26151fc04cadae38b20ad67ab241",  
    api_version="2024-11-20",
    azure_endpoint="https://vals-prod-openai.openai.azure.com"
)


def generate_report_from_scraped_pages():
    """
    Reads text from the scraped pages, sends it to OpenAI,
    and gets a structured JSON output following the HighLevelBusinessWebsiteScrapeReport format.
    """
    try:
        pages_content = load_scraped_website_content()  # Get scraped page content
    except Exception as e:
        raise RuntimeError(f"Error loading scraped website content: {e}")
        
    if not pages_content:
        raise ValueError("No pages found to process.")
    
    # Combine pages text into one message
    joined_pages = "\n\n---PAGE BREAK---\n\n".join(pages_content)

    # JSON structure hint (helps OpenAI understand the expected format)
    structure_hint = """
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

    system_prompt = "You are a helpful assistant that outputs valid JSON only."

    user_prompt = f"""
    I have scraped 3 pages from a company's website. 
    Below is the text. Please read it carefully, then 
    produce a **valid JSON** that matches this structure:
    {structure_hint}

    Fill in the relevant fields with the data you find. If unknown, leave them empty.

    --SCRAPED PAGE CONTENT--
    {joined_pages}

    Remember:
    1) Return **ONLY valid JSON**. No markdown, no extra commentary.
    2) Ensure the JSON keys **exactly match the structure above**.
    """

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0,
        )
        raw_json_output = response.choices[0].message.content
        return raw_json_output
    except Exception as e:
        raise RuntimeError(f"Azure OpenAI API Error: {str(e)}")

def parse_into_pydantic(raw_json_output: str) -> HighLevelBusinessWebsiteScrapeReport:
    """
    Parses OpenAI's JSON response into a valid HighLevelBusinessWebsiteScrapeReport model.
    Ensures the response matches the expected structure.
    """
    try:
        # Convert string response to a Python dictionary
        data_dict = json.loads(raw_json_output)
    except json.JSONDecodeError as e:
        raise ValueError(f"OpenAI returned invalid JSON: {e}")

    try:
        # Validate the JSON against the Pydantic model
        report_model = HighLevelBusinessWebsiteScrapeReport(**data_dict)
        return report_model
    except ValidationError as e:
        raise ValueError(f"JSON does not match the Pydantic model: {e}")

def save_report_to_json(report_model: HighLevelBusinessWebsiteScrapeReport, filename="final_website_report.json"):
    """
    Saves the structured report model into a JSON file.
    """
    try:
        with open(filename, "w", encoding="utf-8") as f:
            f.write(report_model.json(indent=4))
        print(f"✅ Report saved as {filename}")
    except Exception as e:
        raise RuntimeError(f"Failed to save report: {e}")

def main():
    # Step 1: Generate report from scraped pages
    try:
        print("Generating report from scraped pages...")
        raw_json = generate_report_from_scraped_pages()
        print("Raw JSON output received.")
    except Exception as e:
        print(f"Error during generation: {e}")
        return

    # Step 2: Parse JSON into Pydantic model
    try:
        print("Parsing JSON into Pydantic model...")
        report_model = parse_into_pydantic(raw_json)
        print("JSON parsed successfully.")
    except Exception as e:
        print(f"Error during JSON parsing: {e}")
        return

    # Step 3: Save the report to a JSON file
    try:
        print("Saving report to JSON file...")
        save_report_to_json(report_model)
    except Exception as e:
        print(f"Error during file saving: {e}")
        return

    print("Process completed successfully!")

if __name__ == '__main__':
    main()
