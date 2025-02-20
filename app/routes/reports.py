from fastapi import APIRouter
from app.services.openaiProcessor import generate_report_from_scraped_pages, parse_into_pydantic

router = APIRouter()

@router.get("/generate-report")
def generate_report_endpoint():
    raw_json = generate_report_from_scraped_pages()
    report_model = parse_into_pydantic(raw_json)
    return report_model.dict()
