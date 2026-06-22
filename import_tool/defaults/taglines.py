"""Generated copy for restaurant.* and pages.* fields the source can't supply.

Rather than maintaining N nearly-identical full template sets (one per cuisine
bucket), we keep ONE set of copy templates parameterized by a human-readable
cuisine label (e.g. "Sichuan", "Chinese", "Asian") drawn from CUISINE_LABELS.
Templates use {name}, {name_short}, {city}, {state}, {cuisine} placeholders
filled in from already-known restaurant data — this mirrors the
double-injection convention build.py already uses for pages.home.hero_sub etc,
so the generated strings are plain templates, not pre-resolved text.
"""

CUISINE_LABELS = {
    "sichuan":    "Sichuan",
    "chinese":    "Chinese",
    "japanese":   "Japanese",
    "korean":     "Korean",
    "thai":       "Thai",
    "vietnamese": "Vietnamese",
    "generic":    "Asian",
}


def cuisine_label(bucket):
    return CUISINE_LABELS.get(bucket, "Asian")


# Every value here is a *template string* — gap-fill fills {placeholders} from
# already-known RestaurantData fields (name, name_short, city, state) plus the
# detected `cuisine` label. The output is written into config.json verbatim
# (still containing literal {{restaurant.name_short}}-style tokens where the
# existing config.json convention already used them — see hero_sub / welcome_text).
RESTAURANT_TEMPLATES = {
    "tagline":            "Authentic {cuisine} Cuisine",
    "description":        "Authentic {cuisine} cuisine in {city}, {state} — {name}. Dine in or order online today!",
    "description_plain":  "Authentic {cuisine} cuisine in {city}, {state}. {name} — fresh ingredients, bold flavors.",
    "footer_description": "Authentic {cuisine} cuisine — bold flavors, fresh ingredients, made to order.",
}

PAGES_TEMPLATES = {
    "home": {
        "hero_headline":       "Authentic {cuisine} <em>Cuisine</em>",
        "hero_sub":            "{{{{restaurant.name_short}}}}: Authentic {cuisine} Cuisine in {{{{contact.address_city}}}}",
        "ingredients_eyebrow": "Real Ingredients — Fresh &amp; Delicious",
        "ingredients_h2":      "Quality you can taste in every dish",
        "ingredients_body":    "At {{{{restaurant.name_short}}}}, we are committed to providing our customers with authentic {cuisine} cuisine using only the freshest ingredients. Every dish is made to order — for a truly satisfying dining experience.",
        "instagram_eyebrow":   "Follow Along",
        "instagram_headline":  "Follow us on Instagram",
        "reviews_eyebrow":     "Reviews",
        "reviews_h2":          "See What Customers are Saying",
    },
    "menu": {
        "subtitle":         "Our Menu",
        "meta_description": "Browse the full {{{{restaurant.name}}}} menu. Order online for carryout.",
        "og_description":   "Explore our full menu. Order online for carryout.",
        "h1":               "Our Full Menu",
        "tagline":          "Come hungry — here's everything we're serving up.",
        "eyebrow":          "Come Hungry",
    },
    "gallery": {
        "meta_description": "See photos of {{{{restaurant.name}}}}'s dishes. Authentic {cuisine} cuisine in {{{{contact.address_city}}}}, {{{{contact.address_state}}}}.",
        "og_description":   "Photos of {{{{restaurant.name}}}} dishes.",
        "eyebrow":          "Our Kitchen",
    },
    "location": {
        "welcome_text": "Welcome to {{{{restaurant.name}}}}. We serve authentic {cuisine} cuisine made from the freshest ingredients. We are located on {{{{contact.address_street}}}}. Order online for carryout today!",
        "atmosphere":   "Casual Dining",
        "eyebrow":          "Find Us",
        "tagline":          "Find us, call us, or send a message — we'd love to hear from you.",
        "contact_eyebrow":  "Get In Touch",
        "contact_h2":       "Contact Form",
    },
    "catering": {
        "meta_description": "Let {{{{restaurant.name}}}} cater your next event. Call {{{{contact.phone_display}}}} to plan your order.",
        "og_description":   "Authentic {cuisine} food for your event. Call {{{{contact.phone_display}}}} to plan your catering order.",
        "h1":               "Let us cater your event!",
        "offer_h2":         "What we offer",
    },
}


def render_restaurant_copy(bucket, name, city, state):
    cuisine = cuisine_label(bucket)
    return {
        key: tpl.format(cuisine=cuisine, name=name, city=city, state=state)
        for key, tpl in RESTAURANT_TEMPLATES.items()
    }


def render_pages_copy(bucket):
    """Returns the pages.* dict. Templates that reference {{restaurant.*}} /
    {{contact.*}} keep those tokens literal (escaped as {{{{...}}}} in the
    Python format-string source) so build.py's double-pass inject resolves
    them at build time — exactly like the hand-written config.json today."""
    cuisine = cuisine_label(bucket)
    return {
        page: {key: tpl.format(cuisine=cuisine) for key, tpl in fields.items()}
        for page, fields in PAGES_TEMPLATES.items()
    }
