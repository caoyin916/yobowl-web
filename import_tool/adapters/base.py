"""Adapter contract — one module per POS/ordering platform.

An adapter's job is purely mechanical: fetch the source page and report
exactly what it literally contains, mapped onto the common RestaurantData
schema. It must NOT guess, infer, or fill gaps — that's gapfill.py's job.
Fields the source doesn't provide should be left empty/None.
"""
from abc import ABC, abstractmethod

from import_tool.schema import RestaurantData


class AdapterError(Exception):
    """Raised when a source page can't be parsed — e.g. its structure changed."""


class Adapter(ABC):
    PLATFORM = ""  # short slug, e.g. "chowbus"

    @abstractmethod
    def matches(self, url: str) -> bool:
        """Return True if this adapter knows how to handle the given URL."""

    @abstractmethod
    def fetch(self, url: str) -> str:
        """Retrieve the raw source document (HTML/JSON/etc.) for the URL."""

    @abstractmethod
    def parse(self, raw: str, source_url: str) -> RestaurantData:
        """Parse the raw source document into a RestaurantData snapshot."""
