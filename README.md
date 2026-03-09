# Email-finder
A simple async repo that finds public business emails from company websites using Olostep.

## What it does

For each company website:

1. Normalizes the website
2. Builds a fallback list of likely contact pages
3. Uses Olostep Maps to discover more URLs
4. Filters likely contact/about/support/legal/team pages
5. Uses Olostep Batch with `@olostep/extract-emails`
6. Retrieves JSON output for each processed page
7. Aggregates and deduplicates emails per company
8. Writes CSV and JSON outputs

## Install

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

## Input CSV

Must contain one of:

- `website`
- `url`
- `domain`

Optional company column:

- `company`
- `name`

Example:

```csv
company,website
Stripe,stripe.com
Brex,brex.com
Notion,notion.so
```

## Configuration

`.env` only needs:

```bash
OLOSTEP_API_KEY=your_olostep_api_key_here
```

All other runtime values (timeouts, batch size, map depth, etc.) are in:

- `config/settings.py`

## Run

Default usage:

```bash
python main.py
```

Optional input/output overrides:

```bash
python main.py --input companies.csv --output-dir output
```

## Output

- `output/company_results.csv`
- `output/company_results.json`
- `output/page_results.csv`
- `output/page_results.json`
- `output/errors.json`
