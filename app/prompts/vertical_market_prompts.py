def get_vertical_market_system_message() -> str:
    return (
        "You are an expert analyst specializing in vertical market software companies. "
        "Analyze the provided business report and return a valid JSON object with "
        "'reasoning' (string) and 'final_answer' (boolean) keys."
    )


def get_vertical_market_prompt(report_text: str) -> str:
    return f"""I have a business report in JSON format generated from a website analysis.

{report_text}

Based on this report, determine if the company is a vertical market software company.
A vertical market software company develops software specifically for a particular industry or niche.

Respond with a JSON object containing:
- "reasoning": a string explaining your thought process
- "final_answer": a boolean (true or false)

Do not include any extra text before or after the JSON."""
