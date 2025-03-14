from pydantic import BaseModel

class VerticalMarketCheckRequest(BaseModel):
    report_text: str
    retries: int = 3

class VerticalMarketCheckResponse(BaseModel):
    reasoning: str
    final_answer: str