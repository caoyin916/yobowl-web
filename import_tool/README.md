# import_tool

Onboarding helper that turns a restaurant's existing POS/online-ordering page
into a draft `config.json` for this template pipeline (`config.json` →
`build.py` → `dist/`, see the repo root `CLAUDE.md`).

No source page has everything a site needs — this tool is built around that
gap: it extracts what it can, mechanically derives what it safely can
(phone/address/hours formatting, maps links, cuisine-bucket copy), and clearly
flags what only a human can supply (real photography, social links, API keys).

## Usage

```bash
python3 -m import_tool.cli import --url "https://pos.chowbus.com/online-ordering/store/Show-Mian/11436" --slug show-mian-plano
```

This writes everything to `onboarding/<slug>/` (gitignored — scratch space,
never this repo's live `config.json`):

| File | Purpose |
|---|---|
| `raw_source.html` | Cached page fetch — re-runs read this instead of hitting the network (`--refetch` forces a re-download) |
| `menu.json` | Full structured menu: sections → items, bilingual names, prices, photos, sequence |
| `import.json` | The draft config plus `_meta` (source/fetch info) and `_field_provenance` (which fields came from the source vs. were generated vs. need a human) — also serves as the merge baseline for re-imports |
| `config.json` | The live, human-editable draft. This is what eventually becomes *that restaurant's* `config.json` in its own repo |

Other subcommands: `fetch` (cache the page only), `gapfill` (re-run
parsing + gap-fill from the cached page), `merge` (see below). Run any
subcommand with `--help` for its flags.

## The `TODO_MANUAL:` convention

Fields nothing in the source can supply — hero/logo/menu photography,
Instagram links, the Web3Forms key, Google review URL, the restaurant's actual
domain, etc. — are written as a greppable sentinel:

```
"TODO_MANUAL: homepage hero background photo"
```

Array fields carry the sentinel per-entry — e.g. each of the 3 `reviews[]`
drafted gets its own `TODO_MANUAL: paste a real customer review here`, and each
of the 6 `media.instagram_photos` gets its own `TODO_MANUAL: Instagram photo URL`
— so a single `grep TODO_MANUAL` still surfaces every one that needs attention.

This mirrors the `"REPLACE_WITH_YOUR_WEB3FORMS_KEY"` placeholder convention
already used in this repo's `config.json`. Find every one of them with:

```bash
grep -n TODO_MANUAL onboarding/<slug>/config.json
```

## Re-running imports safely (`merge`)

Source data changes (menu/price updates, new hours), but by the time you
re-import, a human has likely already hand-edited the draft `config.json`
(resolved `TODO_MANUAL:` markers, tweaked copy, etc). A naive overwrite would
destroy that work — so re-imports go through a three-way merge instead:

- **base** = `import.json` from the last accepted import
- **mine** = the current `config.json` (possibly hand-edited since)
- **theirs** = a freshly generated draft

| Comparison | Result |
|---|---|
| `mine` differs from `base` | **KEPT** — a human edited it; never overwritten |
| `mine == base`, `theirs` differs | **UPDATED** — safe to take the new value |
| field is new in `theirs` | **ADDED** |

```bash
python3 -m import_tool.cli import  --url "<store-url>" --slug <slug>     # generates import.draft.json alongside the existing config.json
python3 -m import_tool.cli merge   --slug <slug> --dry-run               # preview: key: old -> new [KEPT/UPDATED/ADDED]
python3 -m import_tool.cli merge   --slug <slug>                         # apply, and promote the draft to the new baseline
```

## What's configurable

Everything restaurant-specific in the template is driven by `config.json` (see
the repo root `CLAUDE.md`) plus a handful of asset directories that hold the
actual photos. This is the canonical map of all of it — use it to sanity-check
a generated draft, or as a checklist when hand-editing `config.json` for a new
restaurant.

### `config.json` fields

| Section | Keys | What they control |
|---|---|---|
| `restaurant.*` | `name`, `name_short`, `initials`, `tagline`, `description`, `description_plain`, `footer_description` | Restaurant identity and copy used across headlines, meta tags, JSON-LD, and the footer |
| | `cuisine_schema` | Raw `"A", "B", "C"` string injected into the JSON-LD `servesCuisine` array |
| | `price_range`, `copyright_year`, `accepts_reservations` | JSON-LD `priceRange`/`acceptsReservations` and the footer copyright year |
| | `has_catering` | `"True"`/`"False"` — set `"False"` if this restaurant doesn't cater and `build.py` will drop `Catering.html` and its nav/footer links entirely |
| `contact.*` | `phone_display`, `phone_e164`, `phone_tel` | Phone number in human-display, E.164, and `tel:`-link formats |
| | `address_street`, `address_street_display`, `address_full`, `address_city`, `address_state`, `address_zip`, `address_country`, `address_landmark` | Address components shown on the Location page and in JSON-LD |
| | `coordinates_lat`, `coordinates_lng` | JSON-LD `geo` coordinates |
| `hours.*` | `schema_opens`, `schema_closes`, `days_schema` | JSON-LD `OpeningHoursSpecification` (raw `"Monday", "Tuesday", ...` string for `dayOfWeek`) |
| | `display`, `days_display`, `carryout_display` | Human-readable hours strings shown on the Location page |
| `site.*` | `domain`, `base_url` | Canonical domain/URL — used in JSON-LD `@id`/`url` and canonical `<link>` tags |
| | `web3forms_key` | Web3Forms access key that routes the contact form's submissions |
| | `google_review_url` | Destination of the "leave a review" link |
| `links.*` | `order_online` | Online-ordering URL — nav CTA + JSON-LD `potentialAction` |
| | `instagram`, `instagram_handle` | Instagram profile link/handle — leave `instagram` empty to hide the homepage Instagram section entirely |
| | `maps`, `maps_embed` | Google Maps link + embed-iframe URL |
| `media.*` | `hero_bg`, `logo`, `og_image`, `ingredients_photo`, `menu_image_1`, `menu_image_2`, `catering_menu`, `location_storefront_image` | Paths to the photos described in the asset-directory table below |
| | `instagram_photos` | Array of 6 Instagram feed-photo URLs |
| | `google_fonts_url` | Google Fonts stylesheet URL |
| `pages.home.*` | `hero_headline`, `hero_sub` | Homepage hero heading/subheading |
| | `ingredients_eyebrow`, `ingredients_h2`, `ingredients_body` | "Real Ingredients" section copy |
| | `instagram_eyebrow`, `instagram_headline` | Instagram section copy |
| | `reviews_eyebrow`, `reviews_h2` | Reviews section heading |
| `pages.menu.*` | `eyebrow`, `subtitle`, `h1`, `tagline` | Menu page heading copy |
| | `meta_description`, `og_description` | Menu page SEO meta / social-share description |
| `pages.gallery.*` | `eyebrow` | Gallery page section label |
| | `meta_description`, `og_description` | Gallery page SEO meta / social-share description |
| `pages.location.*` | `eyebrow`, `tagline`, `welcome_text` | Location page-head and intro copy |
| | `contact_eyebrow`, `contact_h2` | Contact-form section heading copy |
| | `cuisine_tags`, `atmosphere` | Tag chips and dining-style label shown in the info block |
| `pages.catering.*` | `h1`, `offer_h2` | Catering page heading copy |
| | `meta_description`, `og_description` | Catering page SEO meta / social-share description (also reused for the Twitter card) |
| `gallery_admin.*` | `site_key`, `passcode` | IndexedDB namespace and passcode for the hidden gallery-admin upload preview — `passcode` is drafted as a `TODO_MANUAL:` sentinel and flagged `manual` so every onboarded site doesn't ship with the same guessable default |
| `reviews[]` | `stars`, `text`, `author` (×3 by convention) | Homepage review cards — each entry's `text`/`author` is drafted as a `TODO_MANUAL:` sentinel and flagged `manual` so placeholder review copy can't slip through to customers |
| `theme.*` | `accent`, `accent_dark`, `ember`, `gold`, `chili_from`, `cream`, `cream_deep`, `ink`, `font_head`, `font_body` | CSS custom-property color palette and font families — drafted with a working "Chili Oil & Porcelain" starting palette (hex values can't carry `TODO_MANUAL:` sentinels without breaking the build) but flagged `manual` so it still shows up in the "Needs manual input" summary as a prompt to customize it for the new restaurant's actual branding |

### Asset directories

Photos are files, not config strings, so they don't show up in `import.json` →
`_field_provenance` — the import tool can extract a logo URL from the source
page (when available) but can't supply real photography. Each working asset
directory ships with generic placeholder images (`*-placeholder.svg`) so a
fresh clone builds and runs out of the box; replace them with your own photos
before going live.

| Directory | Holds | Referenced via | Recommended format / size |
|---|---|---|---|
| `gallery-photo/` | Public gallery photos | `gallery-photo/photos.json` (lists the filenames to display) | JPG/WebP, ~1000×750 landscape |
| `menu-photo/` | Featured dish photos + catering menu | `media.menu_image_1`, `media.menu_image_2`, `media.catering_menu` | JPG/WebP ~800×600 for dish photos; a PDF or tall image for the catering menu (leave `catering_menu` empty if you don't offer one) |
| `location-photo/` | Storefront / parking-guide photo | `media.location_storefront_image` | JPG/WebP ~1200×800 |
| `branding-photo/` | Hero background, logo, social-share image, "real ingredients" photo | `media.hero_bg`, `media.logo`, `media.og_image`, `media.ingredients_photo` | `hero_bg` ~1600×900; `logo` square, transparent PNG; `ingredients_photo` ~800×600; **`og_image` must be a real JPG/PNG ≥1200×630 — Facebook/X/etc. don't render SVG images in social-share previews**, so swap the placeholder for a raster photo even if you keep SVGs elsewhere |

`uploads/` is the owner's upload scratch space (per the repo root `CLAUDE.md`
— not referenced by any public page) and ships empty (with a `.gitkeep`); it
isn't part of what's "configurable" and doesn't need photography to launch.

### Sourcing real branding assets (`hero_bg`, `logo`, `og_image`)

These three are the hardest to fill because they need to be on-brand, not
just "a photo of the food":

- **Check the restaurant's existing online-ordering page first.** Most POS/
  ordering platforms (HungerRush, Menufy, Toast, Square, Chowbus, etc.) host
  the restaurant's own logo and a wide branding/hero banner on their CDN —
  view the page source and look for `<meta property="og:image">`, the hero
  `<img>`/`background-image`, and any `logo`/`brand` image tags. If found,
  download these directly (`curl -o branding-photo/<name>.png "<cdn-url>"`)
  rather than substituting stock photography — it's the restaurant's actual
  branding and usually already sized close to what's needed.
- A logo pulled this way is often a flat graphic on a white background (not
  transparent) — that's fine for `media.logo` in the hero plate, but won't
  look right anywhere a transparent PNG/SVG is expected.
- A wide wordmark/banner graphic (rather than a photo) can still work for
  `hero_bg`/`og_image` — `object-fit: cover` will scale and center-crop it —
  but expect it to look softer than a real photo since it gets upscaled to
  fill the hero band. Note this tradeoff for the client rather than silently
  shipping a blurry hero.
- If nothing usable turns up on the ordering page, leave the generic
  placeholder and flag it as a manual to-do rather than guessing with an
  unrelated stock photo.

### Document asset provenance per site

For each `sites/<slug>/`, add a short `README.md` with a table of which
`media.*` keys (and gallery/Instagram photos) point at real assets vs. the
generic placeholders, where the real ones came from, and what's still needed
before launch (web3forms key, real reviews, missing photos, etc.). See
`sites/yobowl-carrollton/README.md` for the format — this is what tells your
partner (or the client) exactly what's left to do for *that* restaurant.

## Adding a new platform adapter

Adapters live in `import_tool/adapters/` and implement the `Adapter` ABC
(`adapters/base.py`):

```python
class Adapter(ABC):
    PLATFORM = "yourplatform"
    def matches(self, url: str) -> bool: ...      # does this URL belong to your platform?
    def fetch(self, url: str) -> str: ...          # return the raw page source
    def parse(self, raw: str, source_url: str) -> RestaurantData: ...  # -> common schema
```

`RestaurantData` / `MenuData` / `MenuSection` / `MenuItem` (in
`import_tool/schema.py`) are the **common intermediate schema** every adapter
must produce — this is what keeps adapters thin and mechanical ("what does
the source literally say") while all inference/defaults policy stays
centralized in `gapfill.py`. Leave a field empty/`None`/`[]` if the source
doesn't have it; don't guess inside the adapter.

Raise `AdapterError` (from `adapters/base`) with a clear message if the page's
structure doesn't match what you expect — e.g. "X changed their page format,
the adapter needs updating" — rather than returning partial garbage silently.

Then register it in `adapters/__init__.py`'s `ADAPTERS` list. `chowbus.py` is
a complete worked example, including notes on how it pulls structured data out
of a JS-framework page without a headless browser (Chowbus server-renders its
data as React Server Component streaming JSON — look for similar patterns in
other Next.js-based platforms like Menusifu, HungerRush, or Toast before
reaching for browser automation).

## Cuisine-bucket defaults

`gapfill.py` heuristically detects a cuisine bucket (sichuan / chinese /
japanese / korean / thai / vietnamese / generic) from menu item/section names
— see `defaults/cuisine_tags.py` (`detect_cuisine`, `CUISINE_DEFAULTS` for
`cuisine_schema`/`cuisine_tags`) and `defaults/taglines.py` (copy templates for
`restaurant.*` and `pages.*`, parameterized by the bucket's display label). The
guess and matched keywords are recorded in `import.json` → `_meta` so a human
can correct it — check `_meta.cuisine_bucket` if the generated copy reads oddly.
