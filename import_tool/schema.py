"""Common intermediate schema — the contract between adapters and gap-fill/merge.

Every platform adapter parses its source into a RestaurantData (+ optional
MenuData). Adapters stay thin and mechanical: they report only what the
source literally provides, leaving empty strings / None for anything absent.
All inference and default-generation policy lives in gapfill.py.
"""
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class SourceAddress:
    street: str = ""
    street_2: str = ""
    city: str = ""
    state: str = ""
    zip: str = ""
    country: str = "US"
    landmark: str = ""
    lat: Optional[float] = None
    lng: Optional[float] = None


@dataclass
class DayHours:
    day: str                                  # "monday".."sunday"
    intervals: list = field(default_factory=list)   # [("11:00", "20:45"), ...]
    closed: bool = False


@dataclass
class MenuItem:
    name: str
    foreign_name: str = ""
    description: str = ""
    price: Optional[str] = None               # kept as string ("7.95") to avoid float rounding
    image_url: str = ""
    sequence: int = 0
    source_id: str = ""                       # platform's native item id — stable re-import diffing


@dataclass
class MenuSection:
    name: str
    foreign_name: str = ""
    description: str = ""
    image_url: str = ""
    sequence: int = 0
    items: list = field(default_factory=list)        # list[MenuItem]
    source_id: str = ""


@dataclass
class MenuData:
    source_platform: str
    source_url: str
    fetched_at: str                           # ISO timestamp
    sections: list = field(default_factory=list)     # list[MenuSection]


@dataclass
class RestaurantData:
    """Adapter output / gap-fill input — a platform-agnostic restaurant snapshot."""
    source_platform: str
    source_url: str
    fetched_at: str
    name: str = ""
    name_foreign: str = ""
    phone_e164: str = ""                       # e.g. "+14695738619"
    address: SourceAddress = field(default_factory=SourceAddress)
    hours: list = field(default_factory=list)        # list[DayHours]
    order_online_url: str = ""
    timezone: str = ""
    logo_url: str = ""
    hero_image_url: str = ""
    menu: Optional[MenuData] = None
    raw_extra: dict = field(default_factory=dict)    # platform-specific scraps worth keeping
