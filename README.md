# VMS Analyzer — AI-Powered Company Classification Pipeline

![Python](https://img.shields.io/badge/Python-3.11-3776AB?style=flat&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?style=flat&logo=fastapi&logoColor=white)
![OpenAI](https://img.shields.io/badge/OpenAI-GPT--4o--mini%20%7C%20o3--mini-412991?style=flat&logo=openai&logoColor=white)
![Firecrawl](https://img.shields.io/badge/Firecrawl-Web%20Scraping-FF6B35?style=flat)
![Pydantic](https://img.shields.io/badge/Pydantic-v2-E92063?style=flat&logo=pydantic&logoColor=white)

> Given any company URL, this pipeline scrapes their website, generates a structured business report, and uses a reasoning AI model to determine whether the company is a **Vertical Market Software (VMS)** company — fully automated, end-to-end.

---

## What Is This?

Vertical Market Software companies build software for a single, specific industry (e.g. software exclusively for dental clinics, or exclusively for auto dealerships). Identifying them manually is time-consuming and inconsistent.

This project automates that process. You give it a URL. It gives you a `true` or `false` verdict — with reasoning.

It was built as the backend intelligence layer for a larger VMS research and investment tool.

---

## Live Pipeline

```
URL Input
   │
   ▼
Firecrawl (scrape + clean website content)
   │
   ▼
GPT-4o-mini (generate structured JSON business report)
   │
   ▼
o3-mini reasoning model (classify: is this a VMS company?)
   │
   ▼
{ "final_answer": true, "reasoning": "..." }
```

---

## Key Features

- **Multi-page scraping** — crawls up to N pages per domain, deduplicates content, and strips noise (images, nav, dropdowns)
- **Structured AI reports** — GPT-4o-mini produces a consistent JSON schema covering business model, products, target market, pricing, and team
- **Reasoning-based classification** — o3-mini evaluates the report and returns a verdict with a full explanation, not just a label
- **Caching** — scraped content is saved locally so re-runs skip the crawl step unless `--force-crawl` is passed
- **Dual-mode** — runs as a REST API (for the frontend) or a CLI tool (for quick local analysis)
- **Output files** — every run saves deduplicated data, the business report, and the classification result to `output/{domain}/`

---

## Tech Stack

| Layer | Tool | Why |
|---|---|---|
| API Framework | FastAPI | Async, fast, auto-generates /docs |
| Report Generation | OpenAI `gpt-4o-mini` | Cost-efficient, structured output |
| Classification | OpenAI `o3-mini` | Reasoning model — explains its verdict |
| Web Scraping | Firecrawl API | Handles JS-heavy sites, returns clean markdown |
| Data Validation | Pydantic v2 | Strict schema enforcement across all I/O |
| Environment | python-dotenv | Clean secret management |

---

## Project Structure

```
URLs-Validation/
├── app/
│   ├── main.py                            # FastAPI app + CLI entry point
│   ├── services/
│   │   ├── openaiProcessor.py             # Report generation (gpt-4o-mini)
│   │   └── verticalMarketProcessor.py     # VMS classification (o3-mini)
│   ├── routes/
│   │   ├── firecrawlScrapping.py          # POST /api/scrape/scrape
│   │   ├── buildReport.py                 # POST /api/report/generate-report
│   │   └── verticalMarketCheckerRouter.py # POST /api/vertical-market-check/...
│   ├── prompts/
│   │   ├── report_prompts.py              # Prompts for business report generation
│   │   └── vertical_market_prompts.py     # Prompts for VMS classification
│   ├── models/
│   │   ├── reportsModels.py               # Pydantic report schema
│   │   └── url_validation.py              # URL input validation
│   └── utils/
│       ├── firecrawlApp.py                # Scraping + content cleaning logic
│       ├── validators.py                  # URL format + redirect validation
│       └── file_operations.py             # File read/write utilities
├── tests/
│   ├── conftest.py
│   └── unit/
├── output/                                # Auto-created — one folder per domain
│   └── {domain}/
│       ├── deduplicated_data.json
│       ├── report.json
│       └── vertical_market_check.json
├── openai_tester.py                       # Quick API key verification script
├── .env                                   # API keys (never committed)
└── requirements.txt
```

---

## Getting Started

### 1. Clone and install

```bash
git clone https://github.com/alexanderluo10890/URLs-Validation.git
cd URLs-Validation
python -m venv .venv
.venv\Scripts\activate        # Windows
source .venv/bin/activate     # macOS/Linux
pip install -r requirements.txt
```

### 2. Add your API keys

Create a `.env` file in the root:

```
OPENAI_API_KEY=sk-your-openai-key
FIRECRAWL_API_KEY=fc-your-firecrawl-key
```

Get keys at: [platform.openai.com](https://platform.openai.com) · [firecrawl.dev](https://firecrawl.dev)

### 3. Verify setup

```bash
python openai_tester.py
```

---

## Running the App

### API mode (connects to the frontend)

```bash
python -m app.main --mode api
```

Runs at `http://localhost:8000` — interactive docs at `/docs`.

### CLI mode (run directly from terminal)

```bash
python -m app.main --mode cli --url https://www.example.com
```

| Flag | Default | Description |
|---|---|---|
| `--url` | required | Company website to analyze |
| `--max-pages` | 3 | Number of pages to crawl |
| `--force-crawl` | false | Re-crawl even if cached data exists |
| `--retries` | 3 | OpenAI retry attempts on failure |

---

## API Endpoints

### `POST /api/scrape/scrape`
Scrape a website and return cleaned content.

```json
// Request
{ "url": "https://www.example.com", "max_pages": 3, "force_crawl": false }

// Response
{ "message": "Content loaded successfully", "content": "..." }
```

### `POST /api/report/generate-report`
Generate a structured JSON business report from scraped text.

```json
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

### `POST /api/vertical-market-check/vertical-market-check`
Classify whether a company is a VMS company.

```json
// Response
{
  "reasoning": "The company develops software exclusively for the hospitality industry...",
  "final_answer": true
}
```

---

## What I Learned

- **Prompt engineering for structured output** — getting GPT-4o-mini to return consistent, deeply nested JSON required careful schema design and iterative prompt tuning
- **Reasoning models behave differently** — o3-mini doesn't respond well to over-constrained prompts; giving it room to reason and then extracting the verdict produced far better results than asking for a direct answer
- **Web scraping is messy** — real company sites are noisy; building a cleaning layer on top of Firecrawl's output (deduplication, stripping irrelevant sections) significantly improved AI output quality
- **Caching matters in AI pipelines** — scraping and inference are both slow and costly; saving intermediate outputs made iteration 10x faster during development

---

## Tests

```bash
pytest tests/
```

---

## Output

Every run saves three files to `output/{domain}/`:

| File | Contents |
|---|---|
| `deduplicated_data.json` | Cleaned scraped content |
| `report.json` | Structured business report from GPT-4o-mini |
| `vertical_market_check.json` | VMS verdict + reasoning from o3-mini |
