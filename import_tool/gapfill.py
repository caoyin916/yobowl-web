"""Builds a draft config.json from RestaurantData, classifying every leaf as:

  - "source"    — the adapter read it directly off the platform page
  - "generated" — mechanically derived (phone/address/hours formatting, maps
                  URLs) or filled from a cuisine-bucket template/default
                  (defaults/taglines.py, defaults/cuisine_tags.py, theme
                  palette, reviews placeholder)
  - "manual"    — nothing in the source can supply this; written as a
                  greppable "TODO_MANUAL: <what's needed>" sentinel, mirroring
                  the project's existing "REPLACE_WITH_YOUR_WEB3FORMS_KEY"
                  convention (see config.json -> site.web3forms_key)

`build_draft_config()` returns (config_dict, provenance) where `provenance`
maps every dot-path to one of the three classifications above — this is what
merge.py persists as `_field_provenance` so re-imports know which fields a
human has since edited by hand.
"""
import re
from datetime import datetime, timezone
from urllib.parse import quote_plus

from import_tool.defaults.cuisine_tags import CUISINE_DEFAULTS, detect_cuisine
from import_tool.defaults.taglines import cuisine_label, render_pages_copy, render_restaurant_copy

WEEKDAY_ORDER = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
WEEKDAY_ABBREV = {
    "monday": "Mon", "tuesday": "Tue", "wednesday": "Wed", "thursday": "Thu",
    "friday": "Fri", "saturday": "Sat", "sunday": "Sun",
}

# This repo's actual "Chili Oil & Porcelain" palette (see css/styles.css :root
# and CLAUDE.md) — a more defensible generic starting point than an unrelated scheme.
DEFAULT_THEME = {
    "accent": "#be2f25", "accent_dark": "#8c1c14", "ember": "#e89033", "gold": "#d6a437",
    "chili_from": "#cf3622", "cream": "#f8f2e8", "cream_deep": "#f1e8d8", "ink": "#211a15",
    "font_head": "Montserrat", "font_body": "Open Sans",
}
DEFAULT_GOOGLE_FONTS_URL = (
    "https://fonts.googleapis.com/css2?family=Montserrat:wght@600;700;800"
    "&family=Open+Sans:wght@400;600&display=swap"
)


def todo(description):
    """Greppable manual-input sentinel — see module docstring."""
    return f"TODO_MANUAL: {description}"


# ---- mechanical formatters --------------------------------------------------

def to_schema_array_string(items):
    """`["A", "B", "C"]` -> the raw string `A", "B", "C` that gets injected
    inside an existing `["{{...}}"]` JSON-LD array — the convention verified
    in template/_schema_restaurant.html (cuisine_schema / days_schema)."""
    return '", "'.join(items)


def _phone_digits(raw):
    digits = re.sub(r"\D", "", raw or "")
    if len(digits) == 11 and digits.startswith("1"):
        digits = digits[1:]
    return digits if len(digits) == 10 else None


def format_phone(raw):
    """Source phone (any punctuation/E.164) -> the three config.json phone fields."""
    digits = _phone_digits(raw)
    if not digits:
        return None
    area, mid, last = digits[:3], digits[3:6], digits[6:]
    return {
        "phone_display": f"({area}) {mid}-{last}",
        "phone_e164": f"+1-{area}-{mid}-{last}",
        "phone_tel": f"+1{area}{mid}{last}",
    }


def compute_initials(name):
    words = [w for w in re.split(r"\s+", (name or "").strip()) if w]
    return "".join(w[0].upper() for w in words[:2])


def derive_name_short(name):
    """Strips a trailing parenthetical location qualifier, e.g.
    'Show Mian 小面 (Plano)' -> 'Show Mian 小面' — common on multi-location
    platform listings. A human should still sanity-check this."""
    return re.sub(r"\s*\([^)]*\)\s*$", "", name or "").strip() or name


def _format_time_12h(hhmm):
    try:
        h, m = (int(p) for p in hhmm.split(":")[:2])
    except (ValueError, AttributeError):
        return hhmm
    period = "AM" if h < 12 else "PM"
    h12 = h % 12 or 12
    return f"{h12}:{m:02d}{period}" if m else f"{h12}{period}"


def _format_interval(intervals):
    if not intervals:
        return "Closed"
    start, end = intervals[0]
    return f"{_format_time_12h(start)}–{_format_time_12h(end)}"


def _day_groups(hours):
    """Groups consecutive days (Mon..Sun order) that share identical interval
    sets. Returns [(day_list, intervals), ...]. No wrap-around merging — kept
    simple since this is a generated, human-reviewed field."""
    groups = []
    for dh in hours:
        if groups and groups[-1][1] == dh.intervals:
            groups[-1][0].append(dh.day)
        else:
            groups.append(([dh.day], dh.intervals))
    return groups


def _format_day_range(days):
    if len(days) == 1:
        return WEEKDAY_ABBREV.get(days[0], days[0].title())
    return f"{WEEKDAY_ABBREV.get(days[0], days[0].title())}–{WEEKDAY_ABBREV.get(days[-1], days[-1].title())}"


def build_hours(hours):
    """Returns the full hours.* dict. The largest day-group becomes the
    'schema' group (schema_opens/schema_closes/days_schema/days_display);
    `display`/`carryout_display` summarize every group — mirrors the existing
    config.json convention (see hours.display vs hours.days_schema)."""
    if not hours:
        return None
    groups = _day_groups(sorted(hours, key=lambda d: WEEKDAY_ORDER.index(d.day) if d.day in WEEKDAY_ORDER else 99))
    schema_group = max(groups, key=lambda g: len(g[0]))
    schema_intervals = schema_group[1]
    display = " · ".join(f"{_format_day_range(days)} {_format_interval(iv)}" for days, iv in groups)
    return {
        "schema_opens": schema_intervals[0][0] if schema_intervals else "",
        "schema_closes": schema_intervals[0][1] if schema_intervals else "",
        "days_schema": to_schema_array_string([d.title() for d in schema_group[0]]),
        "display": display,
        "days_display": _format_day_range(schema_group[0]),
        "carryout_display": display,
    }


def build_address_and_links(addr, order_online_url):
    """Returns (contact_fields, links_fields) derived from SourceAddress."""
    street = addr.street
    street_display = f"{street}, {addr.street_2}" if addr.street_2 else street
    street_full = f"{street} {addr.street_2}" if addr.street_2 else street
    address_full = f"{street_full}, {addr.city}, {addr.state} {addr.zip}".strip(", ")
    query = quote_plus(address_full)
    contact = {
        "address_street": street_full,
        "address_street_display": street_display,
        "address_city": addr.city,
        "address_state": addr.state,
        "address_zip": addr.zip,
        "address_country": addr.country,
        "address_landmark": addr.landmark,
        "address_full": address_full,
        "coordinates_lat": f"{addr.lat:.4f}" if addr.lat is not None else "",
        "coordinates_lng": f"{addr.lng:.4f}" if addr.lng is not None else "",
    }
    links = {
        "order_online": order_online_url,
        "maps": f"https://www.google.com/maps/search/?api=1&query={query}",
        "maps_embed": f"https://maps.google.com/maps?q={query}&z=15&output=embed",
    }
    return contact, links


# ---- top-level builder -------------------------------------------------------

def build_draft_config(data, slug):
    """Returns (config_dict, provenance) — see module docstring for the
    "source"/"generated"/"manual" classification that `provenance` records."""
    config = {}
    provenance = {}

    def put(path, value, kind):
        parts = path.split(".")
        node = config
        for part in parts[:-1]:
            node = node.setdefault(part, {})
        node[parts[-1]] = value
        provenance[path] = kind

    cuisine_bucket, matched_keywords = detect_cuisine(data.menu)
    cuisine_defaults = CUISINE_DEFAULTS[cuisine_bucket]
    name_short = derive_name_short(data.name)
    city, state = data.address.city, data.address.state

    # --- restaurant.* ---
    put("restaurant.name", data.name, "source")
    put("restaurant.name_short", name_short, "generated")
    put("restaurant.initials", compute_initials(name_short), "generated")
    for key, value in render_restaurant_copy(cuisine_bucket, name_short, city, state).items():
        put(f"restaurant.{key}", value, "generated")
    put("restaurant.cuisine_schema", to_schema_array_string(cuisine_defaults["cuisine_schema"]), "generated")
    put("restaurant.price_range", "$$", "generated")
    put("restaurant.copyright_year", str(datetime.now(timezone.utc).year), "generated")
    put("restaurant.accepts_reservations", "False", "generated")
    put("restaurant.has_catering", "True", "generated")

    # --- contact.* (+ links.maps*) ---
    contact_fields, link_fields = build_address_and_links(data.address, data.order_online_url)
    if data.address.street or data.address.city:
        # The source supplied an address object — empty sub-fields (e.g. a
        # blank landmark/suite) are valid source data, not gaps to flag.
        for key, value in contact_fields.items():
            put(f"contact.{key}", value, "source")
    else:
        for key in contact_fields:
            put(f"contact.{key}", todo("street address — source page didn't provide one"), "manual")
    phone = format_phone(data.phone_e164)
    if phone:
        for key, value in phone.items():
            put(f"contact.{key}", value, "source")
    else:
        for key in ("phone_display", "phone_e164", "phone_tel"):
            put(f"contact.{key}", todo("restaurant phone number — source page didn't provide one"), "manual")

    # --- hours.* ---
    hours_fields = build_hours(data.hours)
    if hours_fields:
        for key, value in hours_fields.items():
            put(f"hours.{key}", value, "source")
    else:
        for key in ("schema_opens", "schema_closes", "days_schema", "display", "days_display", "carryout_display"):
            put(f"hours.{key}", todo("business hours — source page didn't provide them"), "manual")

    # --- site.* ---
    put("site.domain", todo("the restaurant's actual domain name, e.g. example.com"), "manual")
    put("site.base_url", todo("https://www.<domain> once the domain is known"), "manual")
    put("site.web3forms_key", "REPLACE_WITH_YOUR_WEB3FORMS_KEY", "manual")
    put("site.google_review_url", todo("Google Maps review/listing URL for this location"), "manual")

    # --- links.* ---
    if link_fields["order_online"]:
        put("links.order_online", link_fields["order_online"], "source")
    else:
        put("links.order_online", todo("online ordering URL"), "manual")
    put("links.instagram", todo("Instagram profile URL"), "manual")
    put("links.instagram_handle", todo("Instagram @handle"), "manual")
    put("links.maps", link_fields["maps"], "generated")
    put("links.maps_embed", link_fields["maps_embed"], "generated")

    # --- media.* (every image needs real photography/curation — see plan) ---
    image_fields = {
        "hero_bg": "homepage hero background photo",
        "logo": "restaurant logo",
        "og_image": "social share preview image",
        "ingredients_photo": "homepage 'real ingredients' section photo",
        "menu_image_1": "homepage featured-dish photo #1",
        "menu_image_2": "homepage featured-dish photo #2",
        "catering_menu": "catering menu PDF or image (leave empty if none)",
        "location_storefront_image": "storefront / parking photo for the Location page",
    }
    if data.logo_url:
        put("media.logo", data.logo_url, "source")
    else:
        put("media.logo", todo(image_fields.pop("logo")), "manual")
    for key, description in image_fields.items():
        put(f"media.{key}", todo(description), "manual")
    put("media.instagram_photos", [todo("Instagram photo URL") for _ in range(6)], "manual")
    put("media.google_fonts_url", DEFAULT_GOOGLE_FONTS_URL, "generated")

    # --- pages.* (cuisine-bucket copy templates) ---
    for page, fields in render_pages_copy(cuisine_bucket).items():
        for key, value in fields.items():
            put(f"pages.{page}.{key}", value, "generated")
    put("pages.location.cuisine_tags", cuisine_defaults["cuisine_tags"], "generated")

    # --- gallery_admin.* ---
    put("gallery_admin.site_key", re.sub(r"[^a-z0-9]+", "", slug.lower()) or "restaurant", "generated")
    put("gallery_admin.passcode", todo("choose a private admin passcode for the gallery upload tool"), "manual")

    # --- reviews[] (placeholder text would otherwise ship straight to customers) ---
    put("reviews", [
        {"stars": "★★★★★",
         "text": todo("paste a real customer review here"),
         "author": todo("customer name, e.g. — Jane D.")}
        for _ in range(3)
    ], "manual")

    # --- theme.* (working starting palette — flagged so the owner reviews/customizes it) ---
    put("theme", dict(DEFAULT_THEME), "manual")

    config["_meta"] = {
        "source_platform": data.source_platform,
        "source_url": data.source_url,
        "fetched_at": data.fetched_at,
        "slug": slug,
        "cuisine_bucket": cuisine_bucket,
        "cuisine_bucket_label": cuisine_label(cuisine_bucket),
        "cuisine_bucket_matched_keywords": matched_keywords,
        "cuisine_bucket_note": (
            "Heuristically detected from menu text — please verify and adjust "
            "restaurant.cuisine_schema / pages.location.cuisine_tags if it's off."
        ),
    }

    return config, provenance
