import re
from typing import Any, List

EMAIL_RE = re.compile(r"\b[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[A-Za-z]{2,}\b")


def normalize_email(email: str) -> str:
    return email.strip().strip(".,;:()[]{}<>\"'").lower()


def extract_emails_from_payload(payload: Any) -> List[str]:
    found: set[str] = set()

    def walk(value: Any) -> None:
        if value is None:
            return

        if isinstance(value, str):
            for match in EMAIL_RE.findall(value):
                found.add(normalize_email(match))
            return

        if isinstance(value, list):
            for item in value:
                walk(item)
            return

        if isinstance(value, dict):
            for item in value.values():
                walk(item)
            return

    walk(payload)
    return sorted(found)
