import argparse
import logging
from pathlib import Path

from config.settings import Settings
from src.email_finder import LeadEmailFinder
from utils.io import (
    ensure_output_dir,
    load_targets_csv,
    write_company_results_csv,
    write_json,
    write_page_results_csv,
)
from utils.logger import setup_logging

logger = logging.getLogger(__name__)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Find public business emails from company websites using Olostep."
    )
    parser.add_argument(
        "--input",
        default="companies.csv",
        help="Path to input CSV with a website/url/domain column.",
    )
    parser.add_argument(
        "--output-dir",
        default="output",
        help="Directory where output files will be written.",
    )
    return parser


async def async_main() -> int:
    args = build_parser().parse_args()
    setup_logging()

    try:
        settings = Settings.from_env()
        output_dir = ensure_output_dir(args.output_dir)
        targets = load_targets_csv(args.input)
    except (ValueError, FileNotFoundError) as exc:
        logger.error("%s", exc)
        return 1

    if not targets:
        logger.error("No valid targets found in the input CSV.")
        return 1

    logger.info("Loaded %s target websites", len(targets))

    finder = LeadEmailFinder(settings)
    company_results, page_results, errors = await finder.run(targets)

    write_company_results_csv(output_dir / "company_results.csv", company_results)
    write_page_results_csv(output_dir / "page_results.csv", page_results)
    write_json(output_dir / "company_results.json", company_results)
    write_json(output_dir / "page_results.json", page_results)
    write_json(output_dir / "errors.json", errors)

    companies_with_emails = sum(1 for item in company_results if item.emails)
    total_unique_emails = sum(len(item.emails) for item in company_results)

    logger.info("Done")
    logger.info("Companies processed: %s", len(company_results))
    logger.info("Companies with emails: %s", companies_with_emails)
    logger.info("Total unique emails found: %s", total_unique_emails)
    logger.info("Output written to: %s", Path(output_dir).resolve())

    return 0
