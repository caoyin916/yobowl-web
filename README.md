# Restaurant Website Template

A reusable static-site pipeline that builds a complete restaurant website from
a single `config.json`. One shared `template/` of HTML/CSS/JS, one Python
build script, one config file per restaurant — no framework, no npm.

Pages included: **Home · Menu · Gallery · Location & Contact · Catering**
(Catering is optional — disabled via `config.json`).

---

## Onboarding a new restaurant

### Step 1 — Gather this information from the restaurant

| Category | What you need |
|---|---|
| **Identity** | Restaurant name (full and short form), initials (2–3 letters), tagline, 1–2 sentence description, cuisine type(s), price range ($ / $$ / $$$) |
| **Contact** | Phone number, full street address (with city / state / zip), GPS coordinates (lat/lng for the map pin) |
| **Hours** | Opening and closing time, days of the week open, carryout-specific hours if different |
| **Online ordering** | URL of the restaurant's existing ordering page (HungerRush, Toast, Chowbus, etc.) |
| **Social** | Instagram profile URL and handle (leave blank to hide the Instagram section) |
| **Reviews** | 3 real customer quotes (text + author label) |
| **Domain** | The restaurant's domain name and full `https://www.` base URL |
| **Google** | Google Maps link + embed URL, Google Business "leave a review" URL |

### Step 2 — Run the import tool (optional but saves time)

The import tool can auto-draft most of `config.json` from the restaurant's
existing POS/ordering page:

```bash
python3 -m import_tool.cli import \
  --url "https://<their-ordering-page>" \
  --slug <restaurant-slug>
```

This writes a draft to `onboarding/<slug>/config.json`. Run
`grep -n TODO_MANUAL onboarding/<slug>/config.json` to see every field that
still needs a human answer. See `import_tool/README.md` for the full
import workflow, including how to re-run safely after menu changes.

### Step 3 — Fill in photos

Place photos in `sites/<slug>/` under the appropriate asset directory:

| Directory | What goes here | Key `config.json` field(s) | Recommended size |
|---|---|---|---|
| `branding-photo/` | Hero background, logo, OG/social-share image, "fresh ingredients" photo | `media.hero_bg`, `media.logo`, `media.og_image`, `media.ingredients_photo` | `hero_bg` ~1600×900 · `logo` transparent PNG · **`og_image` must be JPG/PNG ≥ 1200×630** (social platforms don't render SVG) |
| `menu-photo/` | Featured dish photos and catering menu image | `media.menu_image_1`, `media.menu_image_2`, `media.catering_menu` | JPG/WebP ~800×600 |
| `location-photo/` | Storefront or parking-guide photo | `media.location_storefront_image` | JPG/WebP ~1200×800 |
| `gallery-photo/` | Public photo gallery images + `photos.json` manifest | listed in `gallery-photo/photos.json` | JPG/WebP ~1000×750 |

**Tip:** check the restaurant's existing ordering page first — most platforms
(HungerRush, Menufy, Toast, Chowbus) host the restaurant's own logo and hero
banner on their CDN. Grab them from the page's `<meta og:image>` or hero
`<img>` source before going hunting for new photos.

### Step 4 — Build and preview

```bash
python3 build.py --site <slug>
cd sites/<slug>/dist && python3 -m http.server 8080
# open http://localhost:8080
```

---

## `config.json` field reference

Every field in `config.json` maps to a `{{key}}` placeholder in `template/`.
The root `config.json` is a generic skeleton with placeholder values — copy it
into `sites/<slug>/config.json` and fill it in.

### `restaurant.*`

| Key | Used for |
|---|---|
| `name` | Full restaurant name — appears in page titles, JSON-LD, headings |
| `name_short` | Shorter form used inline (e.g. "At {{name_short}}, we…") |
| `initials` | 2–3 letter monogram shown in the brand mark (nav/footer) |
| `tagline` | Short one-liner — subtitle on the hero |
| `description` | ~2 sentences, SEO meta description and JSON-LD |
| `description_plain` | Plain-text version (no HTML) for JSON-LD `description` |
| `footer_description` | Short blurb under the logo in the footer |
| `cuisine_schema` | Raw string injected into JSON-LD `servesCuisine`, e.g. `"Chinese", "Asian"` |
| `price_range` | `$` / `$$` / `$$$` — JSON-LD `priceRange` |
| `copyright_year` | Year shown in the footer copyright line |
| `accepts_reservations` | `"True"` or `"False"` — JSON-LD |
| `has_catering` | `"True"` or `"False"` — set `"False"` to drop `Catering.html` and all nav/footer links to it |

### `contact.*`

| Key | Used for |
|---|---|
| `phone_display` | Human-readable phone, e.g. `(972) 555-1234` |
| `phone_e164` | E.164 format, e.g. `+1-972-555-1234` — JSON-LD |
| `phone_tel` | `tel:` link value, e.g. `+19725551234` |
| `address_street` | Street address |
| `address_street_display` | Street address as shown to visitors (can include Suite/Ste) |
| `address_full` | Full one-line address — shown on Location page |
| `address_city`, `address_state`, `address_zip`, `address_country` | Address components for JSON-LD |
| `address_landmark` | Optional landmark text (e.g. "next to H-Mart") |
| `coordinates_lat`, `coordinates_lng` | GPS decimal coordinates for JSON-LD `geo` |

### `hours.*`

| Key | Used for |
|---|---|
| `schema_opens`, `schema_closes` | Opening/closing time in `HH:MM` for JSON-LD `OpeningHoursSpecification` |
| `days_schema` | Raw `"Monday", "Tuesday", …` string for JSON-LD `dayOfWeek` |
| `display` | Human-readable hours line, e.g. `Mon–Sun 11AM–9PM` |
| `days_display` | Days-only summary, e.g. `Mon – Sun` |
| `carryout_display` | Carryout-specific hours if they differ from dine-in |

### `site.*`

| Key | Used for |
|---|---|
| `domain` | Bare domain, e.g. `yourrestaurant.com` |
| `base_url` | Full canonical URL, e.g. `https://www.yourrestaurant.com` |
| `web3forms_key` | Web3Forms access key — routes the Location-page contact form submissions to the restaurant's email. Generate one at web3forms.com |
| `google_review_url` | "Leave a review" link on the Location page |

### `links.*`

| Key | Used for |
|---|---|
| `order_online` | Online-ordering URL — nav CTA and JSON-LD `potentialAction` |
| `instagram` | Instagram profile URL — leave empty to hide the Instagram section entirely |
| `instagram_handle` | Handle without `@` — shown as `@handle` in the section |
| `maps` | Google Maps link — "Get Directions" button |
| `maps_embed` | Google Maps embed URL for the iframe on the Location page |

### `media.*`

| Key | File location | Used for |
|---|---|---|
| `hero_bg` | `branding-photo/` | Hero background image (full-width) |
| `logo` | `branding-photo/` | Logo shown in the hero "logo plate" |
| `og_image` | `branding-photo/` | Social-share preview image (must be JPG/PNG ≥ 1200×630) |
| `ingredients_photo` | `branding-photo/` | Photo in the "fresh ingredients" feature section |
| `menu_image_1` | `menu-photo/` | First featured menu/dish photo on the Menu page |
| `menu_image_2` | `menu-photo/` | Second featured menu/dish photo |
| `catering_menu` | `menu-photo/` | Catering menu image or PDF shown on the Catering page |
| `location_storefront_image` | `location-photo/` | Storefront or parking-guide photo on the Location page |
| `instagram_photos` | URLs | Array of 6 Instagram feed-photo URLs shown in the Instagram section |
| `google_fonts_url` | — | Google Fonts stylesheet URL (change to swap fonts) |

### `pages.*`

Heading and copy overrides per page:

| Section | Keys |
|---|---|
| `pages.home` | `hero_headline`, `hero_sub`, `ingredients_eyebrow`, `ingredients_h2`, `ingredients_body`, `instagram_eyebrow`, `instagram_headline`, `reviews_eyebrow`, `reviews_h2` |
| `pages.menu` | `eyebrow`, `subtitle`, `h1`, `tagline`, `meta_description`, `og_description` |
| `pages.gallery` | `eyebrow`, `meta_description`, `og_description` |
| `pages.location` | `eyebrow`, `tagline`, `welcome_text`, `contact_eyebrow`, `contact_h2`, `cuisine_tags`, `atmosphere` |
| `pages.catering` | `h1`, `offer_h2`, `meta_description`, `og_description` |

### `gallery_admin.*`

| Key | Used for |
|---|---|
| `site_key` | IndexedDB namespace for the admin photo-upload preview (unique per site) |
| `passcode` | Passcode to unlock admin mode at `Gallery.html#admin` — set a real passcode, not the default `"admin"` |

### `reviews[]`

Array of 3 objects, each with `stars`, `text`, and `author`. These are the
homepage review cards — use real customer quotes.

### `theme.*`

CSS custom-property values that set the site's color palette:

| Key | Default | Controls |
|---|---|---|
| `accent` | `#be2f25` | Primary brand color (buttons, highlights) |
| `accent_dark` | `#8c1c14` | Darker shade of accent (hover states) |
| `ember` | `#e89033` | Secondary warm color (eyebrow labels) |
| `gold` | `#d6a437` | Accent-2 (star ratings, subtle highlights) |
| `chili_from` | `#cf3622` | Gradient start color |
| `cream` | `#f8f2e8` | Page background |
| `cream_deep` | `#f1e8d8` | Slightly darker background for alternating bands |
| `ink` | `#211a15` | Body text color |
| `font_head` | `Montserrat` | Heading / UI font (Google Fonts) |
| `font_body` | `Open Sans` | Body text font (Google Fonts) |

---

## Repo layout

| Path | Purpose |
|---|---|
| `template/` | Shared HTML/CSS/JS — every restaurant site is built from this |
| `config.json` | Generic skeleton / field reference (placeholder values) |
| `build.py` | Render pipeline: `template/` + `config.json` → `dist/` |
| `sites/<slug>/` | Per-restaurant working folder (gitignored) — `config.json` + asset dirs + `dist/` preview |
| `examples/` | Complete, filled-in example sites (real config + real photos) |
| `onboarding/<slug>/` | Import-tool draft output (gitignored) — scratch space before promoting to `sites/<slug>/` |
| `import_tool/` | Onboarding helper — drafts `config.json` from a restaurant's existing ordering page |
| `buzzai/` | Buzz-AI company marketing/landing page (separate from the restaurant pipeline) |
