from __future__ import annotations

from typing import Dict, List, Optional

import httpx


class MapsClient:
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
                "Content-Type": "application/json",
            },
        )

    async def aclose(self) -> None:
        await self._client.aclose()

    async def __aenter__(self) -> "MapsClient":
        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:
        await self.aclose()

    async def map_urls(
        self,
        url: str,
        *,
        top_n: int,
        include_subdomain: bool,
    ) -> List[str]:
        all_urls: List[str] = []
        cursor: Optional[str] = None

        while True:
            payload: Dict[str, object] = {
                "url": url,
                "top_n": top_n,
                "include_subdomain": include_subdomain,
            }
            if cursor:
                payload["cursor"] = cursor

            response = await self._client.post("/v1/maps", json=payload)
            response.raise_for_status()
            data = response.json()

            for item in data.get("urls", []) or []:
                if item:
                    all_urls.append(str(item))

            cursor = data.get("cursor")
            if not cursor:
                break

        return self._unique_preserve_order(all_urls)

    @staticmethod
    def _unique_preserve_order(values: List[str]) -> List[str]:
        seen = set()
        output: List[str] = []
        for value in values:
            if value in seen:
                continue
            seen.add(value)
            output.append(value)
        return output
