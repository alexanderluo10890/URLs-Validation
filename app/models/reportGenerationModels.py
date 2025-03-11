from pydantic import BaseModel

class ReportGenerationRequest(BaseModel):
    pages_text: str
    retries: int = 3

class ReportGenerationResponse(BaseModel):
    report: dict
