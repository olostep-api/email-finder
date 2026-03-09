from dataclasses import dataclass
import os

from dotenv import load_dotenv

load_dotenv()

API_BASE_URL = "https://api.olostep.com"
PARSER_ID = "@olostep/extract-emails"
MAP_TOP_N = 50
MAX_PAGES_PER_SITE = 8
MAX_BATCH_ITEMS = 100
INCLUDE_SUBDOMAIN = False
REQUEST_TIMEOUT_SECONDS = 60
BATCH_POLL_INTERVAL_SECONDS = 5
BATCH_POLL_TIMEOUT_SECONDS = 600
MAP_CONCURRENCY = 5


@dataclass(frozen=True)
class Settings:
    api_key: str
    api_base_url: str = API_BASE_URL
    parser_id: str = PARSER_ID
    map_top_n: int = MAP_TOP_N
    max_pages_per_site: int = MAX_PAGES_PER_SITE
    max_batch_items: int = MAX_BATCH_ITEMS
    include_subdomain: bool = INCLUDE_SUBDOMAIN
    request_timeout_seconds: int = REQUEST_TIMEOUT_SECONDS
    batch_poll_interval_seconds: int = BATCH_POLL_INTERVAL_SECONDS
    batch_poll_timeout_seconds: int = BATCH_POLL_TIMEOUT_SECONDS
    map_concurrency: int = MAP_CONCURRENCY

    @classmethod
    def from_env(cls) -> "Settings":
        api_key = os.getenv("OLOSTEP_API_KEY", "").strip()
        if not api_key:
            raise ValueError(
                "Missing OLOSTEP_API_KEY. Add it to .env or export it in your shell."
            )

        return cls(api_key=api_key)
