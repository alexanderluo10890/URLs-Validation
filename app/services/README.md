# OpenAI Processor Service

This service provides functionality to crawl websites, process the content using Azure OpenAI, and generate structured business reports.

## Overview

The OpenAI Processor is designed to:

1. Crawl websites and extract content
2. Process the content using Azure OpenAI's GPT-4o model
3. Generate structured JSON reports with business insights
4. Save the reports for further analysis

## Usage

### Basic Usage

To analyze a website and generate a report:

```bash
python -m app.services.openaiProcessor --url https://example.com
```

This will:
1. Crawl the website if no existing data is found
2. Process the content using Azure OpenAI
3. Generate a structured report
4. Save the report as `example_com_report.json`

### Command Line Arguments

| Argument | Description | Default |
|----------|-------------|---------|
| `--url` | URL of the website to crawl and analyze | None |
| `--max-pages` | Maximum number of pages to process | 3 |
| `--force-crawl` | Force a new crawl even if data exists | False |
| `--output` | Custom output filename for the report | `{domain}_report.json` |
| `--retries` | Number of retries for OpenAI API calls | 3 |

### Examples

#### Analyze a website with forced crawling:

```bash
python -m app.services.openaiProcessor --url https://www.example.com --force-crawl
```

#### Limit the number of pages to crawl:

```bash
python -m app.services.openaiProcessor --url https://www.example.com --max-pages 5
```

#### Specify a custom output file:

```bash
python -m app.services.openaiProcessor --url https://www.example.com --output custom_report.json
```

#### Increase the number of retries for API calls:

```bash
python -m app.services.openaiProcessor --url https://www.example.com --retries 5
```

## Testing

To test the OpenAI processor with a simple example:

```bash
python -m app.services.openaiProcessor --url https://www.example.com
```

For testing with a more complex website:

```bash
python -m app.services.openaiProcessor --url https://www.innquest.com --max-pages 2
```

### Viewing Reports

After generating a report, you can view it using:

```bash
# View the entire report
cat example_com_report.json

# View just the first 30 lines
head -n 30 example_com_report.json

# Search for specific sections
grep -A 5 "primary_products_services" example_com_report.json
```

## Report Structure

The generated reports follow a structured format with the following sections:

1. **Overview**
   - Company snapshot (name, headquarters, year founded, leadership)
   - Website summary (pages reviewed, key observations)

2. **Products and Services**
   - Core offerings (primary products/services, features, use cases)
   - Additional solutions (secondary products, integrations)

3. **Market and Audience**
   - Target audience (customer segments, pain points)
   - Competitive landscape (competitors, differentiators)

4. **Business Model and Pricing**
   - Revenue model (model type, pricing tiers)
   - Key partnerships (partners, promotional offers)

5. **Team and Culture**
   - Company culture (mission/values, employee spotlight)
   - Growth/recruitment (career opportunities, expertise)

6. **High-Level Observations and Conclusion**
   - Overall positioning
   - Potential strengths
   - Potential gaps/limitations

## Implementation Details

The processor uses:
- Structured output parsing with OpenAI's `response_format={"type": "json_object"}`
- Pydantic models for validation and type safety
- Error handling with retries for API calls
- Compatibility with both Pydantic v1 and v2

## Troubleshooting

If you encounter issues:

1. **Invalid URL format**: Ensure the URL includes the protocol (http:// or https://)
2. **Crawling errors**: Check network connectivity and website accessibility
3. **API errors**: Verify Azure OpenAI credentials and quota limits
4. **JSON parsing errors**: The report structure may not match the expected format 