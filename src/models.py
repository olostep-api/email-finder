from dataclasses import dataclass, field
from typing import List


@dataclass
class TargetWebsite:
    company: str
    website: str


@dataclass
class PageEmailHit:
    company: str
    website: str
    page_url: str
    emails: List[str] = field(default_factory=list)
    batch_status: str = "completed"
    error: str = ""


@dataclass
class CompanyEmailResult:
    company: str
    website: str
    emails: List[str] = field(default_factory=list)
    pages_scanned: int = 0
    pages_with_hits: int = 0
    status: str = "ok"
    error: str = ""
