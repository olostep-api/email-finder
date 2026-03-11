from __future__ import annotations

from dataclasses import asdict
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

from config.settings import Settings
from src.email_finder import LeadEmailFinder
from utils.io import (
    ensure_output_dir,
    load_targets_csv,
    write_company_results_csv,
    write_json,
    write_page_results_csv,
)

ProgressCallback = Callable[[str], None]


def _emit(progress_callback: Optional[ProgressCallback], message: str) -> None:
    if progress_callback is not None:
        progress_callback(message)


def _default_output_dir() -> Path:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    return Path("output") / "gradio_runs" / f"run_{timestamp}"


async def run_email_finder_service(
    csv_file_path: str | Path,
    output_dir: str | Path | None = None,
    *,
    progress_callback: Optional[ProgressCallback] = None,
) -> Dict[str, Any]:
    _emit(progress_callback, "Pre-check: validating OLOSTEP_API_KEY.")
    settings = Settings.from_env()

    _emit(progress_callback, "Pre-check: validating CSV headers and loading targets.")
    targets = load_targets_csv(csv_file_path)
    if not targets:
        raise ValueError("No valid targets found in the input CSV.")

    _emit(progress_callback, f"Loaded {len(targets)} target websites.")

    resolved_output_dir = ensure_output_dir(output_dir or _default_output_dir())
    _emit(progress_callback, f"Output directory: {resolved_output_dir.resolve()}")

    finder = LeadEmailFinder(settings, progress_callback=progress_callback)
    company_results, page_results, errors = await finder.run(targets)

    company_results_csv = resolved_output_dir / "company_results.csv"
    page_results_csv = resolved_output_dir / "page_results.csv"
    company_results_json = resolved_output_dir / "company_results.json"
    page_results_json = resolved_output_dir / "page_results.json"
    errors_json = resolved_output_dir / "errors.json"

    write_company_results_csv(company_results_csv, company_results)
    write_page_results_csv(page_results_csv, page_results)
    write_json(company_results_json, company_results)
    write_json(page_results_json, page_results)
    write_json(errors_json, errors)

    companies_with_emails = sum(1 for item in company_results if item.emails)
    total_unique_emails = sum(len(item.emails) for item in company_results)
    total_pages_scanned = sum(item.pages_scanned for item in company_results)
    total_pages_with_hits = sum(item.pages_with_hits for item in company_results)

    status_counts: Dict[str, int] = {}
    for item in company_results:
        status_counts[item.status] = status_counts.get(item.status, 0) + 1

    _emit(progress_callback, "Run completed. Results and output files are ready.")

    return {
        "summary": {
            "companies_processed": len(company_results),
            "companies_with_emails": companies_with_emails,
            "total_unique_emails": total_unique_emails,
            "total_pages_scanned": total_pages_scanned,
            "total_pages_with_hits": total_pages_with_hits,
            "status_counts": status_counts,
        },
        "company_results": [asdict(item) for item in company_results],
        "page_results": [asdict(item) for item in page_results],
        "errors": errors,
        "output_dir": str(resolved_output_dir.resolve()),
        "output_files": {
            "company_results_csv": str(company_results_csv.resolve()),
            "page_results_csv": str(page_results_csv.resolve()),
            "company_results_json": str(company_results_json.resolve()),
            "page_results_json": str(page_results_json.resolve()),
            "errors_json": str(errors_json.resolve()),
        },
    }
