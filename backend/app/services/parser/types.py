from dataclasses import dataclass
from datetime import date, datetime, timezone

@dataclass(frozen=True)
class JobEntry:
    id: str = ""
    person_id: str | None = None
    role: str = ""
    company_or_client: dict = None  # {"name": str|None, "is_client": bool}
    location: str | None = None # "city, region, country | remote | null"
    start_date: date | None = None
    end_date: date | None = None
    currently_working: bool = False
    description: str = ""
    
    # Internal / Legacy fields for processing
    bullets: list[str] = None
    technologies: list[str] = None
    employment_type: str | None = None
    notes: str | None = None
    raw_text: str = ""
    confidence_score: float = 0.0
    last_updated: str = ""
    is_current: bool = False  # Legacy support during transition
    duration_months: int | None = None
    client: str | None = None # Legacy support
    date_flag: str | None = None # Internal processing flag

    def __post_init__(self):
        if self.technologies is None:
            object.__setattr__(self, "technologies", [])
        if self.bullets is None:
            object.__setattr__(self, "bullets", [])
        if self.company_or_client is None:
            object.__setattr__(self, "company_or_client", {"name": "Unknown Company", "is_client": False})
        if not self.last_updated:
            object.__setattr__(self, "last_updated", datetime.now(timezone.utc).isoformat() + "Z")
        
        # If location was passed as a dict, convert to string (legacy compatibility)
        if isinstance(self.location, dict):
            parts = [self.location.get(k) for k in ["city", "region", "country"] if self.location.get(k)]
            loc_str = ", ".join(parts)
            if self.location.get("remote"):
                loc_str = f"{loc_str} | remote" if loc_str else "remote"
            object.__setattr__(self, "location", loc_str or None)

    @property
    def company(self):
        return self.company_or_client.get("name") if self.company_or_client else None

    @property
    def title(self):
        return self.role

