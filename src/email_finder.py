from __future__ import annotations

import asyncio
import json
import logging
import time
from typing import Any, Dict, List, Tuple

from config.settings import Settings
from src.batch_scraper import BatchScraper
from src.maps_client import MapsClient
from src.models import CompanyEmailResult, PageEmailHit, TargetWebsite
from utils.email_tools import extract_emails_from_payload
from utils.url_tools import (
    build_fallback_urls,
    is_likely_contact_page,
    pick_best_candidate_urls,
    unique_urls,
)

logger = logging.getLogger(__name__)


class LeadEmailFinder:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    async def run(
        self, targets: List[TargetWebsite]
    ) -> Tuple[List[CompanyEmailResult], List[PageEmailHit], List[Dict[str, str]]]:
        company_state: Dict[str, Dict[str, Any]] = {
            target.website: {
                "company": target.company,
                "emails": set(),
                "pages_scanned": 0,
                "pages_with_hits": 0,
                "errors": [],
            }
            for target in targets
        }

        async with MapsClient(
            api_token=self.settings.api_key,
            base_url=self.settings.api_base_url,
            timeout=self.settings.request_timeout_seconds,
        ) as maps_client, BatchScraper(
            api_token=self.settings.api_key,
            base_url=self.settings.api_base_url,
            timeout=self.settings.request_timeout_seconds,
        ) as batch_scraper:
            candidate_map = await self._collect_candidate_pages(targets, maps_client)
            batch_items, custom_id_to_meta = self._build_batch_items(targets, candidate_map)
            page_results, errors = await self._run_batches(
                batch_scraper=batch_scraper,
                batch_items=batch_items,
                custom_id_to_meta=custom_id_to_meta,
                company_state=company_state,
            )

        company_results = self._build_company_results(targets, company_state)
        return company_results, page_results, errors

    async def _collect_candidate_pages(
        self,
        targets: List[TargetWebsite],
        maps_client: MapsClient,
    ) -> Dict[str, List[str]]:
        semaphore = asyncio.Semaphore(self.settings.map_concurrency)
        output: Dict[str, List[str]] = {}

        async def worker(target: TargetWebsite) -> None:
            async with semaphore:
                fallback_urls = build_fallback_urls(target.website)
                try:
                    mapped_urls = await maps_client.map_urls(
                        target.website,
                        top_n=self.settings.map_top_n,
                        include_subdomain=self.settings.include_subdomain,
                    )
                except Exception as exc:
                    logger.warning("Map failed for %s: %s", target.website, exc)
                    mapped_urls = []

                mapped_contact_pages = [
                    url for url in mapped_urls if is_likely_contact_page(url)
                ]

                homepage = target.website
                remainder = [
                    url
                    for url in unique_urls(fallback_urls + mapped_contact_pages)
                    if url != homepage
                ]

                best_remainder = pick_best_candidate_urls(
                    remainder,
                    max(0, self.settings.max_pages_per_site - 1),
                )

                pages = unique_urls([homepage] + best_remainder)[
                    : self.settings.max_pages_per_site
                ]
                output[target.website] = pages

                logger.info(
                    "Prepared %s candidate pages for %s",
                    len(pages),
                    target.website,
                )

        await asyncio.gather(*(worker(target) for target in targets))
        return output

    def _build_batch_items(
        self,
        targets: List[TargetWebsite],
        candidate_map: Dict[str, List[str]],
    ) -> Tuple[List[Dict[str, str]], Dict[str, Dict[str, str]]]:
        batch_items: List[Dict[str, str]] = []
        custom_id_to_meta: Dict[str, Dict[str, str]] = {}

        for site_index, target in enumerate(targets, start=1):
            pages = candidate_map.get(target.website, [target.website])
            for page_index, page_url in enumerate(pages, start=1):
                custom_id = f"site{site_index:04d}_page{page_index:02d}"
                batch_items.append({"custom_id": custom_id, "url": page_url})
                custom_id_to_meta[custom_id] = {
                    "company": target.company,
                    "website": target.website,
                    "page_url": page_url,
                }

        return batch_items, custom_id_to_meta

    async def _run_batches(
        self,
        batch_scraper: BatchScraper,
        batch_items: List[Dict[str, str]],
        custom_id_to_meta: Dict[str, Dict[str, str]],
        company_state: Dict[str, Dict[str, Any]],
    ) -> Tuple[List[PageEmailHit], List[Dict[str, str]]]:
        page_results: List[PageEmailHit] = []
        errors: List[Dict[str, str]] = []

        for chunk_index, chunk in enumerate(
            self._chunked(batch_items, self.settings.max_batch_items),
            start=1,
        ):
            logger.info(
                "Starting batch %s with %s page URLs",
                chunk_index,
                len(chunk),
            )

            try:
                batch = await batch_scraper.create_batch(
                    chunk,
                    parser_id=self.settings.parser_id,
                )
                batch_id = str(batch["id"])
            except Exception as exc:
                logger.error("Batch creation failed for chunk %s: %s", chunk_index, exc)
                for item in chunk:
                    meta = custom_id_to_meta[item["custom_id"]]
                    self._record_page_result(
                        company_state=company_state,
                        page_results=page_results,
                        errors=errors,
                        company=meta["company"],
                        website=meta["website"],
                        page_url=meta["page_url"],
                        emails=[],
                        batch_status="failed",
                        error=f"Batch creation failed: {exc}",
                    )
                continue

            try:
                await self._wait_until_complete(batch_scraper, batch_id)
            except Exception as exc:
                logger.error("Batch polling failed for %s: %s", batch_id, exc)
                for item in chunk:
                    meta = custom_id_to_meta[item["custom_id"]]
                    self._record_page_result(
                        company_state=company_state,
                        page_results=page_results,
                        errors=errors,
                        company=meta["company"],
                        website=meta["website"],
                        page_url=meta["page_url"],
                        emails=[],
                        batch_status="failed",
                        error=f"Batch polling failed: {exc}",
                    )
                continue

            async for item in batch_scraper.iter_batch_items(
                batch_id,
                status="completed",
                limit=50,
            ):
                custom_id = str(item.get("custom_id", ""))
                retrieve_id = item.get("retrieve_id")
                meta = custom_id_to_meta.get(custom_id)

                if not meta:
                    continue

                if not retrieve_id:
                    self._record_page_result(
                        company_state=company_state,
                        page_results=page_results,
                        errors=errors,
                        company=meta["company"],
                        website=meta["website"],
                        page_url=meta["page_url"],
                        emails=[],
                        batch_status="completed",
                        error="Missing retrieve_id",
                    )
                    continue

                try:
                    retrieved = await batch_scraper.retrieve(
                        str(retrieve_id),
                        formats=("json",),
                    )
                    payload = self._coerce_json_content(retrieved.get("json_content"))
                    emails = extract_emails_from_payload(payload)

                    self._record_page_result(
                        company_state=company_state,
                        page_results=page_results,
                        errors=errors,
                        company=meta["company"],
                        website=meta["website"],
                        page_url=meta["page_url"],
                        emails=emails,
                        batch_status="completed",
                        error="",
                    )
                except Exception as exc:
                    self._record_page_result(
                        company_state=company_state,
                        page_results=page_results,
                        errors=errors,
                        company=meta["company"],
                        website=meta["website"],
                        page_url=meta["page_url"],
                        emails=[],
                        batch_status="completed",
                        error=f"Retrieve failed: {exc}",
                    )

            async for item in batch_scraper.iter_batch_items(
                batch_id,
                status="failed",
                limit=50,
            ):
                custom_id = str(item.get("custom_id", ""))
                meta = custom_id_to_meta.get(custom_id)
                if not meta:
                    continue

                self._record_page_result(
                    company_state=company_state,
                    page_results=page_results,
                    errors=errors,
                    company=meta["company"],
                    website=meta["website"],
                    page_url=meta["page_url"],
                    emails=[],
                    batch_status="failed",
                    error="Batch item failed",
                )

        return page_results, errors

    async def _wait_until_complete(
        self,
        batch_scraper: BatchScraper,
        batch_id: str,
    ) -> None:
        started_at = time.monotonic()

        while True:
            progress = await batch_scraper.get_batch_progress(batch_id)
            logger.info(
                "Batch %s status=%s completed=%s/%s",
                batch_id,
                progress.status,
                progress.completed_urls,
                progress.total_urls,
            )

            if progress.status == "failed":
                raise RuntimeError(f"Batch {batch_id} failed")

            if progress.is_completed:
                return

            if (
                time.monotonic() - started_at
                > self.settings.batch_poll_timeout_seconds
            ):
                raise TimeoutError(
                    f"Batch {batch_id} did not complete within "
                    f"{self.settings.batch_poll_timeout_seconds} seconds"
                )

            await asyncio.sleep(self.settings.batch_poll_interval_seconds)

    def _record_page_result(
        self,
        *,
        company_state: Dict[str, Dict[str, Any]],
        page_results: List[PageEmailHit],
        errors: List[Dict[str, str]],
        company: str,
        website: str,
        page_url: str,
        emails: List[str],
        batch_status: str,
        error: str,
    ) -> None:
        state = company_state[website]
        state["pages_scanned"] += 1

        if emails:
            state["pages_with_hits"] += 1
            state["emails"].update(emails)

        if error:
            state["errors"].append(error)
            errors.append(
                {
                    "company": company,
                    "website": website,
                    "page_url": page_url,
                    "error": error,
                }
            )

        page_results.append(
            PageEmailHit(
                company=company,
                website=website,
                page_url=page_url,
                emails=emails,
                batch_status=batch_status,
                error=error,
            )
        )

    def _build_company_results(
        self,
        targets: List[TargetWebsite],
        company_state: Dict[str, Dict[str, Any]],
    ) -> List[CompanyEmailResult]:
        results: List[CompanyEmailResult] = []

        for target in targets:
            state = company_state[target.website]
            emails = sorted(state["emails"])
            unique_errors = sorted(set(state["errors"]))

            if emails and unique_errors:
                status = "partial"
            elif emails:
                status = "ok"
            elif unique_errors:
                status = "error"
            else:
                status = "no_emails"

            results.append(
                CompanyEmailResult(
                    company=state["company"],
                    website=target.website,
                    emails=emails,
                    pages_scanned=state["pages_scanned"],
                    pages_with_hits=state["pages_with_hits"],
                    status=status,
                    error=" | ".join(unique_errors),
                )
            )

        return results

    @staticmethod
    def _coerce_json_content(raw: Any) -> Any:
        if raw is None:
            return None

        if isinstance(raw, (dict, list)):
            return raw

        if isinstance(raw, bytes):
            raw = raw.decode("utf-8", errors="replace")

        if isinstance(raw, str):
            raw = raw.strip()
            if not raw:
                return None
            try:
                return json.loads(raw)
            except json.JSONDecodeError:
                return {"raw": raw}

        return {"raw": raw}

    @staticmethod
    def _chunked(items: List[Dict[str, str]], size: int) -> List[List[Dict[str, str]]]:
        return [items[i : i + size] for i in range(0, len(items), size)]
