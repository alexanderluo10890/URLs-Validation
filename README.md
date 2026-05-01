# VMS Backend — Vertical Market Software Analyzer

A FastAPI backend that automatically determines whether a company is a **vertical market software company** by scraping their website and analyzing it with AI.

---

## How It Works

The pipeline runs in 3 steps:

```
URL → Scrape (Firecrawl) → Business Report (gpt-4o-mini) → Vertical Market Check (o3-mini)
```

1. **Scrape** — Crawls the company website using Firecrawl, cleans the content (removes images, dropdowns, noise)
2. **Report** — Sends cleaned content to `gpt-4o-mini` and generates a structured JSON business report
3. **Classify** — Sends the report to `o3-mini` (reasoning model) which returns a `true/false` verdict with detailed reasoning

---

## Tech Stack

| Layer | Technology |
|---|---|
| Framework | FastAPI |
| AI — Report Generation | OpenAI `gpt-4o-mini` |
| AI — Classification | OpenAI `o3-mini` |
| Web Scraping | Firecrawl API |
| Data Validation | Pydantic v2 |
| Environment | python-dotenv |
| Server | Uvicorn |

---

## Project Structure

```
URLs-Validation/
├── app/
│   ├── main.py                            # FastAPI app + CLI entry point
│   ├── services/
│   │   ├── openaiProcessor.py             # Report generation (gpt-4o-mini)
│   │   └── verticalMarketProcessor.py     # Vertical market check (o3-mini)
│   ├── routes/
│   │   ├── firecrawlScrapping.py          # POST /api/scrape/scrape
│   │   ├── buildReport.py                 # POST /api/report/generate-report
│   │   └── verticalMarketCheckerRouter.py # POST /api/vertical-market-check/vertical-market-check
│   ├── prompts/
│   │   ├── report_prompts.py              # Prompts for report generation
│   │   └── vertical_market_prompts.py     # Prompts for classification
│   ├── models/
│   │   ├── reportsModels.py               # Pydantic report schema
│   │   └── url_validation.py              # URL validation models
│   └── utils/
│       ├── firecrawlApp.py                # Firecrawl scraping + content cleaning
│       ├── validators.py                  # URL format + redirect validation
│       └── file_operations.py             # File read/write utilities
├── tests/
│   ├── conftest.py
│   └── unit/
├── output/                                # Auto-created — one folder per company
│   └── {domain}/
│       ├── deduplicated_data.json
│       ├── report.json
│       └── vertical_market_check.json
├── openai_tester.py                       # Quick API key verification script
├── .env                                   # Secret keys (never committed)
└── requirements.txt
```

---

## Setup

### 1. Clone and install dependencies

```bash
git clone https://github.com/alexanderluo10890/URLs-Validation.git
cd URLs-Validation
python -m venv .venv
.venv\Scripts\activate        # Windows
source .venv/bin/activate     # macOS/Linux
pip install -r requirements.txt
```

### 2. Configure environment variables

Create a `.env` file in the project root:

```
OPENAI_API_KEY=sk-your-openai-key
FIRECRAWL_API_KEY=fc-your-firecrawl-key
```

- Get your OpenAI API key at **platform.openai.com**
- Get your Firecrawl API key at **firecrawl.dev**

### 3. Verify your OpenAI key

```bash
python openai_tester.py
```

---

## Running the App

### API Mode (for frontend)

```bash
python -m app.main --mode api
```

Server starts at `http://localhost:8000`. Interactive docs at `http://localhost:8000/docs`.

### CLI Mode (terminal pipeline)

```bash
python -m app.main --mode cli --url https://www.example.com
```

| Flag | Default | Description |
|---|---|---|
| `--url` | required | Company website URL |
| `--max-pages` | 3 | Number of pages to crawl |
| `--force-crawl` | false | Re-crawl even if cached data exists |
| `--retries` | 3 | OpenAI API retry attempts |

Output is saved to `output/{domain}/`.

---

## API Endpoints

### `POST /api/scrape/scrape`
Crawl a website and return cleaned text content.

```json
// Request
{ "url": "https://www.example.com", "max_pages": 3, "force_crawl": false }

// Response
{ "message": "Content loaded successfully", "content": "..." }
```

---

### `POST /api/report/generate-report`
Generate a structured business report from scraped content.

```json
// Request
{ "pages_text": "...", "retries": 3, "url": "https://www.example.com" }

// Response
{
  "report": {
    "overview": {},
    "products_and_services": {},
    "market_and_audience": {},
    "business_model_and_pricing": {},
    "team_and_culture": {},
    "high_level_observations_and_conclusion": {}
  }
}
```

---

### `POST /api/vertical-market-check/vertical-market-check`
Determine if a company is a vertical market software company.

```json
// Request
{ "report_text": "...", "retries": 3, "url": "https://www.example.com" }

// Response
{
  "reasoning": "The company develops software specifically for the hospitality industry...",
  "final_answer": true
}
```

---

## Running Tests

```bash
pytest tests/
```

---

## Output Files

Every analysis creates a folder at `output/{domain}/`:

| File | Description |
|---|---|
| `deduplicated_data.json` | Cleaned scraped page content from Firecrawl |
| `report.json` | Structured business report from gpt-4o-mini |
| `vertical_market_check.json` | Classification result from o3-mini |
