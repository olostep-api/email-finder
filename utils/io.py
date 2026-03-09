import csv
import json
from dataclasses import asdict, is_dataclass
from pathlib import Path
from typing import Any, Iterable, List

from src.models import CompanyEmailResult, PageEmailHit, TargetWebsite
from utils.url_tools import normalize_website


def ensure_output_dir(path: str | Path) -> Path:
    output_dir = Path(path)
    output_dir.mkdir(parents=True, exist_ok=True)
    return output_dir


def load_targets_csv(path: str | Path) -> List[TargetWebsite]:
    file_path = Path(path)

    with file_path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        if not reader.fieldnames:
            raise ValueError("Input CSV must have a header row.")

        normalized_fieldnames = {
            field.strip().lower(): field for field in reader.fieldnames if field
        }

        website_key = (
            normalized_fieldnames.get("website")
            or normalized_fieldnames.get("url")
            or normalized_fieldnames.get("domain")
        )
        company_key = normalized_fieldnames.get("company") or normalized_fieldnames.get(
            "name"
        )

        if not website_key:
            raise ValueError(
                "Input CSV must contain one of these columns: website, url, domain"
            )

        targets: List[TargetWebsite] = []
        seen_websites: set[str] = set()

        for row in reader:
            raw_website = (row.get(website_key) or "").strip()
            if not raw_website:
                continue

            website = normalize_website(raw_website)
            if website in seen_websites:
                continue
            seen_websites.add(website)

            company = (row.get(company_key) or "").strip() if company_key else ""
            if not company:
                company = website

            targets.append(TargetWebsite(company=company, website=website))

    return targets


def write_company_results_csv(
    path: str | Path, results: Iterable[CompanyEmailResult]
) -> None:
    file_path = Path(path)
    with file_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "company",
                "website",
                "emails",
                "pages_scanned",
                "pages_with_hits",
                "status",
                "error",
            ],
        )
        writer.writeheader()

        for row in results:
            writer.writerow(
                {
                    "company": row.company,
                    "website": row.website,
                    "emails": ";".join(row.emails),
                    "pages_scanned": row.pages_scanned,
                    "pages_with_hits": row.pages_with_hits,
                    "status": row.status,
                    "error": row.error,
                }
            )


def write_page_results_csv(path: str | Path, results: Iterable[PageEmailHit]) -> None:
    file_path = Path(path)
    with file_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "company",
                "website",
                "page_url",
                "emails",
                "batch_status",
                "error",
            ],
        )
        writer.writeheader()

        for row in results:
            writer.writerow(
                {
                    "company": row.company,
                    "website": row.website,
                    "page_url": row.page_url,
                    "emails": ";".join(row.emails),
                    "batch_status": row.batch_status,
                    "error": row.error,
                }
            )


def write_json(path: str | Path, data: Any) -> None:
    file_path = Path(path)

    def convert(value: Any) -> Any:
        if is_dataclass(value):
            return asdict(value)
        if isinstance(value, list):
            return [convert(item) for item in value]
        if isinstance(value, tuple):
            return [convert(item) for item in value]
        if isinstance(value, dict):
            return {key: convert(item) for key, item in value.items()}
        return value

    with file_path.open("w", encoding="utf-8") as handle:
        json.dump(convert(data), handle, indent=2, ensure_ascii=False)
