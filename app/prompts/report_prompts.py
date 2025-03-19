"""
This module contains the prompts used for report generation with OpenAI.
"""

# Keep the structure hint for reference in prompts
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

def get_system_message() -> str:
    """
    Returns the system message for the OpenAI API.
    
    Returns:
        str: The system message
    """
    return """
You are a helpful assistant that analyzes website content and extracts business information.
Output your response as a JSON object that EXACTLY follows the structure provided by the user.
Do not deviate from the structure. If information is not available, use empty strings for string fields and empty arrays for array fields.
Do not add any explanatory text before or after the JSON.
"""

def get_report_prompt(pages_text: str) -> str:
    """
    Constructs the prompt for OpenAI with the scraped page content.
    
    Args:
        pages_text (str): The scraped page content
        
    Returns:
        str: The prompt for OpenAI
    """
    return f"""
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