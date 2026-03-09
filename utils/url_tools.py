from urllib.parse import urljoin, urlparse, urlunparse

CONTACT_HINTS = [
    "contact",
    "contact-us",
    "about",
    "about-us",
    "support",
    "help",
    "team",
    "company",
    "legal",
    "privacy",
    "terms",
    "careers",
    "jobs",
]

COMMON_CONTACT_PATHS = [
    "/",
    "/contact",
    "/contact-us",
    "/about",
    "/about-us",
    "/support",
    "/help",
    "/team",
    "/company",
    "/legal",
    "/privacy",
    "/terms",
    "/careers",
    "/jobs",
]


def normalize_website(url: str) -> str:
    raw = (url or "").strip()
    if not raw:
        raise ValueError("Website cannot be empty.")

    if not raw.startswith(("http://", "https://")):
        raw = f"https://{raw}"

    parsed = urlparse(raw)
    if not parsed.netloc and parsed.path:
        parsed = urlparse(f"https://{raw.lstrip('/')}")

    scheme = parsed.scheme or "https"
    netloc = parsed.netloc.lower()
    path = parsed.path.rstrip("/")

    return urlunparse((scheme, netloc, path, "", "", ""))


def website_root(url: str) -> str:
    normalized = normalize_website(url)
    parsed = urlparse(normalized)
    return f"{parsed.scheme}://{parsed.netloc}/"


def build_fallback_urls(base_url: str) -> list[str]:
    root = website_root(base_url)
    return unique_urls(urljoin(root, path.lstrip("/")) for path in COMMON_CONTACT_PATHS)


def is_likely_contact_page(url: str) -> bool:
    parsed = urlparse(normalize_website(url))
    path = parsed.path.lower()

    if not path:
        return True

    return any(hint in path for hint in CONTACT_HINTS)


def unique_urls(urls) -> list[str]:
    seen: set[str] = set()
    output: list[str] = []

    for url in urls:
        normalized = normalize_website(str(url))
        if normalized in seen:
            continue
        seen.add(normalized)
        output.append(normalized)

    return output


def pick_best_candidate_urls(urls: list[str], max_items: int) -> list[str]:
    def score(url: str) -> tuple[int, int]:
        path = urlparse(url).path.lower()

        for index, hint in enumerate(CONTACT_HINTS):
            if hint in path:
                return (index, len(url))

        return (999, len(url))

    ranked = sorted(unique_urls(urls), key=score)
    return ranked[:max_items]
