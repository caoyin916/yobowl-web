"""Cuisine-bucket detection and the cuisine_schema / cuisine_tags strings for each bucket.

Detection is necessarily heuristic — gap-fill records the guess plus the
matched keywords in import.json so a human can correct it if it's off.
"""

# Ordered: first matching bucket wins. Keep keyword lists short and high-signal —
# false positives are worse than a fallback to "generic" (which a human will fix anyway).
CUISINE_KEYWORDS = [
    ("sichuan",  ["麻辣", "辣", "川", "重庆", "夫妻肺片", "spicy", "sichuan", "szechuan"]),
    ("chinese",  ["面", "米线", "饺", "包", "炒", "汤", "noodle", "dumpling", "wonton", "rice"]),
    ("japanese", ["ramen", "sushi", "udon", "tempura", "らーめん", "寿司"]),
    ("korean",   ["kimchi", "bibimbap", "bulgogi", "korean", "김치"]),
    ("thai",     ["pad thai", "tom yum", "thai", "curry"]),
    ("vietnamese", ["pho", "banh mi", "vietnamese"]),
]

# cuisine_schema uses the project's `X\", \"Y\", \"Z` convention — see
# to_schema_array_string() in gapfill.py, which wraps these lists.
# cuisine_tags is a plain comma-separated string (build.py auto-derives *_tags_html from it).
CUISINE_DEFAULTS = {
    "sichuan":    {"cuisine_schema": ["Chinese", "Sichuan", "Asian"],            "cuisine_tags": "Asian, Sichuan, Chinese, Noodles, Spicy"},
    "chinese":    {"cuisine_schema": ["Chinese", "Asian"],                       "cuisine_tags": "Asian, Chinese, Noodles, Dumplings"},
    "japanese":   {"cuisine_schema": ["Japanese", "Asian"],                      "cuisine_tags": "Asian, Japanese, Noodles, Sushi"},
    "korean":     {"cuisine_schema": ["Korean", "Asian"],                        "cuisine_tags": "Asian, Korean, BBQ, Noodles"},
    "thai":       {"cuisine_schema": ["Thai", "Asian"],                          "cuisine_tags": "Asian, Thai, Noodles, Curry"},
    "vietnamese": {"cuisine_schema": ["Vietnamese", "Asian"],                    "cuisine_tags": "Asian, Vietnamese, Noodles, Soup"},
    "generic":    {"cuisine_schema": ["Asian"],                                  "cuisine_tags": "Asian, Noodles"},
}


def detect_cuisine(menu_data):
    """Guess a cuisine bucket from menu section/item names. Returns (bucket, matched_keywords)."""
    if menu_data is None:
        return "generic", []

    haystack = []
    for section in menu_data.sections:
        haystack.append(section.name)
        haystack.append(section.foreign_name)
        for item in section.items:
            haystack.append(item.name)
            haystack.append(item.foreign_name)
    text = " ".join(h.lower() for h in haystack if h)

    for bucket, keywords in CUISINE_KEYWORDS:
        matched = [kw for kw in keywords if kw.lower() in text]
        if matched:
            return bucket, matched

    return "generic", []
