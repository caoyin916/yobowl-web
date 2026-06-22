"""Chowbus online-ordering adapter.

Chowbus storefront pages (pos.chowbus.com/online-ordering/store/<name>/<id>)
are a Next.js App Router SPA, but the data is server-rendered into the
initial HTML response as React Server Component "Flight" streaming chunks:

    <script>self.__next_f.push([1,"<index>:<escaped JSON or JSON-ish text>"])</script>

Concatenating the decoded chunk strings reproduces the full payload the page
hydrates from — restaurant identity, address, hours, and the entire menu
tree — as plain text containing JSON objects (some inline, some referenced
via React Flight "$<hexid>" pointers).

Rather than implementing a full Flight wire-format deserializer (an
internal, undocumented format that could change across Next.js versions),
this adapter scans the joined text for JSON objects/arrays whose *shape*
(a known set of keys) identifies them — e.g. "the object with phone_number,
iana_time_zone and an inline address" or "the menus array". This is more
robust to incidental restructuring than reference-graph traversal, and
degrades to a clear AdapterError if Chowbus changes its data shapes.
"""
import json
import re
from datetime import datetime, timezone

from import_tool.adapters.base import Adapter, AdapterError
from import_tool.schema import DayHours, MenuData, MenuItem, MenuSection, RestaurantData, SourceAddress

import requests

_URL_RE = re.compile(r"chowbus\.com/online-ordering/store/([^/?#]+)/(\d+)")
_CHUNK_MARKER = "self.__next_f.push("

_DECODER = json.JSONDecoder()


def _now_iso():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _extract_payload(html):
    """Decode and concatenate all RSC streaming chunks into one text blob.

    Each chunk looks like `self.__next_f.push([1,"<JSON-escaped string>"])`.
    Rather than regex-matching the escaped string (fragile — JSON escaping
    rules are easy to get subtly wrong in a hand-written pattern), we let
    the JSON decoder parse the `[1, "..."]` array directly: it already knows
    how to handle every escape sequence correctly.
    """
    pieces = []
    pos = 0
    while True:
        idx = html.find(_CHUNK_MARKER, pos)
        if idx == -1:
            break
        start = idx + len(_CHUNK_MARKER)
        try:
            value, _ = _DECODER.raw_decode(html, start)
        except (json.JSONDecodeError, ValueError):
            pos = start
            continue
        pos = start
        if isinstance(value, list) and len(value) >= 2 and isinstance(value[1], str):
            pieces.append(value[1])

    if not pieces:
        raise AdapterError(
            "Chowbus page structure changed — no self.__next_f.push([1, \"...\"]) chunks "
            "could be decoded. The adapter's RSC-chunk extraction needs updating."
        )
    return "".join(pieces)


def _find_object_with_keys(text, required_keys, value_checks=None):
    """Scan `text` for the first JSON object containing all `required_keys`,
    optionally validated by `value_checks` (dict of key -> predicate)."""
    value_checks = value_checks or {}
    for m in re.finditer(r"\{", text):
        try:
            value, _ = _DECODER.raw_decode(text, m.start())
        except (json.JSONDecodeError, ValueError):
            continue
        if not isinstance(value, dict):
            continue
        if not all(k in value for k in required_keys):
            continue
        if all(check(value.get(k)) for k, check in value_checks.items()):
            return value
    return None


def _find_value_after_marker(text, marker):
    """Find the literal `marker` substring and parse the JSON value that follows it."""
    idx = text.find(marker)
    if idx == -1:
        return None
    pos = idx + len(marker)
    while pos < len(text) and text[pos] in " \t\r\n":
        pos += 1
    try:
        value, _ = _DECODER.raw_decode(text, pos)
    except (json.JSONDecodeError, ValueError):
        return None
    return value


class ChowbusAdapter(Adapter):
    PLATFORM = "chowbus"

    def matches(self, url):
        return bool(_URL_RE.search(url))

    def fetch(self, url):
        resp = requests.get(
            url,
            headers={"User-Agent": "Mozilla/5.0 (compatible; yobowl-import-tool/1.0)"},
            timeout=30,
        )
        resp.raise_for_status()
        return resp.text

    def parse(self, raw, source_url):
        payload = _extract_payload(raw)
        fetched_at = _now_iso()

        restaurant = _find_object_with_keys(
            payload,
            required_keys=["name", "phone_number", "iana_time_zone", "address"],
            value_checks={"address": lambda v: isinstance(v, dict) and "address_1" in v},
        )
        if restaurant is None:
            raise AdapterError(
                "Chowbus page structure changed — couldn't locate the restaurant object "
                "(expected keys: name, phone_number, iana_time_zone, address). "
                "The adapter's shape-matching needs updating."
            )

        menus = _find_value_after_marker(payload, '"menus":') or []
        menu_data = self._parse_menu(menus, source_url, fetched_at) if menus else None
        hours = self._parse_hours(menus)

        addr = restaurant.get("address") or {}
        address = SourceAddress(
            street=addr.get("address_1", ""),
            street_2=addr.get("address_2", ""),
            city=addr.get("city", ""),
            state=addr.get("state", ""),
            zip=addr.get("zip_code", ""),
            country=addr.get("country", "US"),
            lat=addr.get("latitude"),
            lng=addr.get("longitude"),
        )

        return RestaurantData(
            source_platform=self.PLATFORM,
            source_url=source_url,
            fetched_at=fetched_at,
            name=restaurant.get("name", ""),
            name_foreign=restaurant.get("foreign_name", ""),
            phone_e164=restaurant.get("phone_number", ""),
            address=address,
            hours=hours,
            order_online_url=source_url,
            timezone=restaurant.get("iana_time_zone", ""),
            logo_url=restaurant.get("logo_url", ""),
            hero_image_url="",
            menu=menu_data,
            raw_extra={"chowbus_restaurant_id": restaurant.get("id", "")},
        )

    @staticmethod
    def _parse_menu(menus, source_url, fetched_at):
        # Prefer the menu named "Online Menu" if present; else the first one with categories.
        chosen = None
        for menu in menus:
            if menu.get("name") == "Online Menu" and menu.get("categories"):
                chosen = menu
                break
        if chosen is None:
            chosen = next((m for m in menus if m.get("categories")), menus[0])

        sections = []
        for cat in chosen.get("categories", []):
            items = []
            for mi in cat.get("meal_instances") or []:
                items.append(MenuItem(
                    name=mi.get("name", ""),
                    foreign_name=mi.get("foreign_name", ""),
                    description=mi.get("description", "") or "",
                    price=mi.get("price") or mi.get("menu_price"),
                    image_url=mi.get("image_url", "") or "",
                    sequence=mi.get("sequence_num", 0) or 0,
                    source_id=str(mi.get("id", "")),
                ))
            sections.append(MenuSection(
                name=cat.get("name", ""),
                foreign_name=cat.get("foreign_name", ""),
                description=cat.get("description", "") or "",
                image_url=cat.get("image_url", "") or "",
                sequence=cat.get("sequence", 0) or 0,
                items=items,
                source_id=str(cat.get("id", "")),
            ))

        return MenuData(
            source_platform="chowbus",
            source_url=source_url,
            fetched_at=fetched_at,
            sections=sections,
        )

    @staticmethod
    def _parse_hours(menus):
        """Collect per-day open/close intervals from the chosen menu's menu_hours.

        Chowbus emits one entry per concrete calendar date (e.g. several
        upcoming Fridays), all sharing the same day_of_week + intervals when
        the schedule is regular. We dedupe by (day_of_week, intervals) and
        keep the first interval set seen per day — sufficient for generating
        a weekly display string. Source data with genuinely irregular
        per-date hours would need richer handling; that's out of scope here.
        """
        if not menus:
            return []
        chosen = next((m for m in menus if m.get("menu_hours")), None)
        if chosen is None:
            return []

        by_day = {}
        order = []
        for entry in chosen["menu_hours"]:
            day = entry.get("day_of_week", "")
            if day in by_day:
                continue
            intervals = [
                (iv.get("start_at", ""), iv.get("end_at", ""))
                for iv in entry.get("time_intervals", [])
            ]
            by_day[day] = DayHours(day=day, intervals=intervals, closed=not intervals)
            order.append(day)

        weekday_order = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
        return sorted(by_day.values(), key=lambda d: weekday_order.index(d.day) if d.day in weekday_order else 99)
