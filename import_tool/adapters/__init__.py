"""Adapter registry — auto-selects a platform adapter by URL pattern.

To add support for a new platform (Menusifu, HungerRush, Toast, ...):
  1. Create adapters/<platform>.py implementing the Adapter contract (see base.py)
  2. Add an instance of it to ADAPTERS below
"""
from import_tool.adapters.chowbus import ChowbusAdapter

ADAPTERS = [
    ChowbusAdapter(),
]


def get_adapter_for_url(url, platform=None):
    """Return the adapter that should handle `url`.

    If `platform` is given, look it up by PLATFORM slug (explicit override).
    Otherwise, auto-select the first adapter whose matches(url) returns True.
    """
    if platform:
        for adapter in ADAPTERS:
            if adapter.PLATFORM == platform:
                return adapter
        raise ValueError(f"Unknown platform: {platform!r} (known: {[a.PLATFORM for a in ADAPTERS]})")

    for adapter in ADAPTERS:
        if adapter.matches(url):
            return adapter
    raise ValueError(f"No adapter recognizes URL: {url!r} — pass --platform to force one")
