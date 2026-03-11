# Olostep Email Finder

A lightweight Python workflow to find **public business emails** from company websites using the **Olostep API**.

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
1. normalizes the website URL/domain
2. builds likely contact-related URLs
3. discovers additional pages via Olostep Maps
4. submits selected pages to Olostep Batch
5. extracts emails from structured parser output
6. deduplicates and aggregates results per company

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
- run controls + expandable run details
- progress logs
- company/page/error result views
- downloadable output files

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

- `main.py` - CLI entrypoint
- `app.py` - frontend entrypoint
- `src/app.py` - CLI orchestration
- `src/frontend.py` - Gradio UI
- `src/service.py` - reusable service wrapper for UI runs
- `src/email_finder.py` - core async pipeline
- `src/maps_client.py` - Olostep Maps client
- `src/batch_scraper.py` - Olostep Batch client
- `src/models.py` - data models
- `utils/io.py` - CSV/JSON I/O helpers
- `utils/url_tools.py` - URL normalization and page selection
- `utils/email_tools.py` - email extraction helpers
- `config/settings.py` - settings/env config

## Tech Stack

- Python
- Gradio
- Olostep Maps
- Olostep Batch
- `@olostep/extract-emails`
- CSV / JSON outputs
