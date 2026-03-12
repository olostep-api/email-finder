# Olostep Email Finder

A lightweight Python workflow to find **public business emails** from company websites using the Olostep API.

This project is useful for:
- B2B lead generation
- sales prospecting
- outreach preparation
- market research

![Olostep Email Finder UI](ui.png)

## Quickstart

Create and activate a virtual environment, then install dependencies:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Create `.env` in the project root:

```bash
OLOSTEP_API_KEY=your_olostep_api_key_here
```

Create an API key from the [Olostep API Keys dashboard](https://www.olostep.com/dashboard/api-keys), then place it in `.env`.

Run the frontend:

```bash
python app.py
```

Or run the CLI:

```bash
python main.py --input companies.csv --output-dir output
```

## What It Does

For each target website, the workflow:
1. Normalizes the website URL/domain.
2. Builds likely contact-related URLs.
3. Discovers additional pages via [Olostep Maps](https://docs.olostep.com/features/maps/maps).
4. Submits selected pages to [Olostep Batch](https://docs.olostep.com/features/batches/batches).
5. Extracts emails from structured parser output.
6. Deduplicates and aggregates results per company.

## Run Modes

### Frontend (Gradio UI)

Launch:

```bash
python app.py
```

Custom host/port:

```bash
python app.py --host 0.0.0.0 --port 7860
```

Hot reload while editing:

```bash
gradio app.py
```

UI includes:
- CSV upload
- Run controls + expandable run details
- Progress logs
- Company/page/error result views
- Downloadable output files

### CLI

Default run:

```bash
python main.py
```

Custom input/output:

```bash
python main.py --input input/companies.csv --output-dir output
```

## Input CSV Format

Required column (one of):
- `website`
- `url`
- `domain`

Optional company name column:
- `company`
- `name`

Example:

```csv
company,website
Stripe,stripe.com
Brex,brex.com
Notion,notion.so
```

## Outputs

The workflow writes:
- `output/company_results.csv`
- `output/company_results.json`
- `output/page_results.csv`
- `output/page_results.json`
- `output/errors.json`

## Configuration

Runtime defaults live in `config/settings.py`, including:
- map depth / top_n
- max pages per site
- max batch items
- concurrency
- polling interval and timeout

## Project Structure

```text
.
├── app.py                   # Frontend entrypoint
├── main.py                  # CLI entrypoint
├── companies.csv            # Example input CSV
├── config/
│   └── settings.py          # Settings/env config
├── input/                   # Input files
├── output/                  # Generated outputs
├── src/
│   ├── app.py               # CLI orchestration
│   ├── frontend.py          # Gradio UI
│   ├── service.py           # Reusable service wrapper for UI runs
│   ├── email_finder.py      # Core async pipeline
│   ├── maps_client.py       # Olostep Maps client
│   ├── batch_scraper.py     # Olostep Batch client
│   └── models.py            # Data models
└── utils/
    ├── io.py                # CSV/JSON I/O helpers
    ├── url_tools.py         # URL normalization and page selection
    └── email_tools.py       # Email extraction helpers
```

## Tech Stack

- Python
- Gradio
- Olostep Maps
- Olostep Batch
- `@olostep/extract-emails`
- CSV / JSON outputs
