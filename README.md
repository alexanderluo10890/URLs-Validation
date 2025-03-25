python -m pytest -s -v .\unit\test_links_validation.py

uvicorn app.utils.main:app --reload

python -m app.services.openaiProcessor2 --url "https://www.innquest.com" --max-pages 3