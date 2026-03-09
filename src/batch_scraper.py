from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Literal, Optional, Sequence, Tuple

import httpx

Formats = Sequence[Literal["html", "markdown", "json"]]
ItemStatus = Literal["completed", "failed"]


@dataclass(frozen=True)
class BatchProgress:
    is_completed: bool
    status: str
    total_urls: int
    completed_urls: int


class BatchScraper:
    """
    Async client for the Olostep Batch API.

    Endpoints used:
        - POST /v1/batches
        - GET /v1/batches/{batch_id}
        - GET /v1/batches/{batch_id}/items
        - GET /v1/retrieve
    """

    def __init__(
        self,
        api_token: str,
        base_url: str = "https://api.olostep.com",
        timeout: float = 60.0,
    ) -> None:
        self._client = httpx.AsyncClient(
            base_url=base_url.rstrip("/"),
            timeout=timeout,
            headers={
                "Authorization": f"Bearer {api_token}",
                "Accept": "application/json",
            },
        )

    async def aclose(self) -> None:
        await self._client.aclose()

    async def __aenter__(self) -> "BatchScraper":
        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:
        await self.aclose()

    async def create_batch(
        self,
        items: Sequence[Dict[str, str]],
        *,
        parser_id: str,
    ) -> Dict[str, Any]:
        normalized_items: List[Dict[str, str]] = []
        for it in items:
            if "url" not in it:
                raise ValueError("Each item dict must contain 'url'.")
            normalized_items.append(
                {"url": it["url"], "custom_id": it.get("custom_id", it["url"])}
            )

        payload: Dict[str, Any] = {
            "items": normalized_items,
            "parser": {"id": parser_id},
        }

        r = await self._client.post("/v1/batches", json=payload)
        r.raise_for_status()
        return r.json()

    async def get_batch_progress(self, batch_id: str) -> BatchProgress:
        r = await self._client.get(f"/v1/batches/{batch_id}")
        r.raise_for_status()
        data = r.json()

        status = str(data.get("status", "")).lower()
        total = int(data.get("total_urls") or 0)
        completed = int(data.get("completed_urls") or 0)
        return BatchProgress(
            is_completed=(status == "completed"),
            status=status,
            total_urls=total,
            completed_urls=completed,
        )

    async def list_batch_items(
        self,
        batch_id: str,
        *,
        status: Optional[ItemStatus] = None,
        cursor: Optional[int] = None,
        limit: Optional[int] = None,
    ) -> Dict[str, Any]:
        params: Dict[str, Any] = {}
        if status:
            params["status"] = status
        if cursor is not None:
            params["cursor"] = cursor
        if limit is not None:
            params["limit"] = limit

        r = await self._client.get(f"/v1/batches/{batch_id}/items", params=params)
        r.raise_for_status()
        return r.json()

    async def iter_batch_items(
        self,
        batch_id: str,
        *,
        status: Optional[ItemStatus] = None,
        limit: int = 50,
    ):
        cursor: Optional[int] = None
        while True:
            page = await self.list_batch_items(
                batch_id, status=status, cursor=cursor, limit=limit
            )
            for item in page.get("items", []) or []:
                yield item

            next_cursor = page.get("cursor", None)
            if next_cursor is None:
                break
            cursor = int(next_cursor)

    async def retrieve(
        self,
        retrieve_id: str,
        *,
        formats: Optional[Formats] = ("markdown",),
    ) -> Dict[str, Any]:
        params: List[Tuple[str, str]] = [("retrieve_id", retrieve_id)]
        if formats:
            for f in formats:
                params.append(("formats", f))

        r = await self._client.get("/v1/retrieve", params=params)
        r.raise_for_status()
        return r.json()
