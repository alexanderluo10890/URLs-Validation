"""
This module contains prompts for vertical market analysis.
"""

def get_vertical_market_system_message() -> str:
    """
    Returns the system message for the vertical market analysis.
    
    Returns:
        str: The system message to send to OpenAI
    """
    return (
        "You are an expert analyst specializing in vertical market software companies. "
        "Analyze the provided business report and return a JSON response with the following structure: "
        "{"
        "'is_vertical_market': boolean, "  # Whether the company is a vertical market software company
        "'primary_industry': string, "     # The main industry they serve
        "'evidence': string, "             # Key evidence from the report supporting the conclusion
        "'confidence': number, "           # Confidence level (0-1) in the assessment
        "'notes': string "                 # Any additional notes or observations
        "}"
    )

def get_vertical_market_prompt(report_text: str) -> str:
    """
    Builds the prompt for checking if a company is a vertical market software company.
    
    Args:
        report_text (str): The text of the business report to analyze
        
    Returns:
        str: The complete prompt to send to OpenAI
    """
    return f"""Based on the following business report, determine if this company is a vertical market software company.
A vertical market software company is one that develops software specifically for a particular industry or business sector.

Business Report:
{report_text}

Please analyze the report and provide a JSON response with the following structure:
{{
    "is_vertical_market": boolean,  // Whether the company is a vertical market software company
    "primary_industry": string,     // The main industry they serve
    "evidence": string,             // Key evidence from the report supporting the conclusion
    "confidence": number,           // Confidence level (0-1) in the assessment
    "notes": string                 // Any additional notes or observations
}}

Focus on:
1. Whether their software is industry-specific
2. Their target market and customer base
3. Their product offerings and how they relate to specific industries
4. Their marketing and sales approach
5. Their partnerships and integrations with industry-specific solutions

Provide a clear, evidence-based assessment based on the information in the report.""" 