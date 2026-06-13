# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this project is

A **reusable static-site template + build pipeline for restaurant websites**.
A single `template/` of HTML/CSS/JS gets rendered against a per-restaurant
`config.json` to produce a complete static site in `dist/` — no framework, no
npm, just HTML, CSS, and vanilla JS plus a small Python build script.

This makes it practical to spin up many restaurant sites (menu, gallery,
location/hours, catering, contact form) from the same design system, each
with its own branding, copy, photos, and theme colors.

## The build pipeline

```bash
python3 build.py                  # build root config.json -> dist/
python3 build.py --site <slug>    # build sites/<slug>/config.json -> sites/<slug>/dist/
```

- **`config.json`** — all restaurant-specific data: name, contact info, hours,
  links, media paths, page copy, reviews, gallery admin settings, and theme
  colors. The root `config.json` is a **generic template skeleton** — copy it
  into `sites/<slug>/config.json` and fill it in for a real restaurant.
- **`build.py`** — flattens `config.json` to dot-notation keys (e.g.
  `contact.phone_display`), injects `{{key}}` placeholders into
  `template/*.html`, resolves `{{> nav}}` / `{{> footer}}` /
  `{{> schema_restaurant}}` partials, resolves `{{#if flat.key}}...{{/if}}`
  conditional blocks (see "Optional pages & sections" below), generates
  `css/theme.css` from `template/css/theme.css.tpl` using `theme.*`, then
  copies asset directories into `dist/`. `dist/` is fully wiped and
  regenerated on every build.
- **Asset directories** (`gallery-photo/`, `menu-photo/`, `location-photo/`,
  `branding-photo/`, `uploads/`) are copied into `dist/` in two passes: the
  repo root's generic placeholders go in first as a fallback baseline, then
  `sites/<slug>/<asset-dir>/` is copied on top — any file there with the same
  name as a root placeholder (e.g. `gallery-photo/photos.json`) overrides it.
  **Important**: `build.py` only copies files that already exist — it never
  creates a file just because `config.json` references its name. Any new
  asset must be placed in `sites/<slug>/<asset-dir>/` (a permanent source
  location, sibling to the disposable `dist/`) *before* building, or the
  build will produce a 404 for that reference.

## Running locally

```bash
python3 build.py --site <slug>
cd sites/<slug>/dist && python3 -m http.server 8080
# then open http://localhost:8080/
```

(For the root template skeleton, omit `--site <slug>` and serve `dist/`.)

## Multi-restaurant layout

| Path | Purpose |
|------|---------|
| `template/` | Shared HTML/CSS/JS source for every restaurant site |
| `config.json` | Generic template skeleton / schema reference (placeholder values) |
| `build.py` | Render pipeline: `template/` + `config.json` -> `dist/` |
| `sites/<slug>/` | **Gitignored** per-restaurant working folder: `config.json` + asset dirs + `dist/` preview. Staging area before a restaurant graduates to its own deploy repo. |
| `onboarding/<slug>/` | **Gitignored** hand-transcribed/import-tool draft configs (raw working notes before promoting to `sites/<slug>/`) |
| `import_tool/` | Onboarding helper that drafts a new restaurant's `config.json` from its existing POS/ordering page — see `import_tool/README.md` for the full field reference and the `TODO_MANUAL:` convention for fields needing human input |
| `examples/yobowl-carrollton/` | Real photos from the original Yo Bowl Carrollton site, kept purely as a size/format/aspect-ratio reference. Not referenced by any `config.json` or copied into `dist/`. |

## File map (`template/`)

| File | Purpose |
|------|---------|
| `index.html` | Home page |
| `Menu.html` | Menu page |
| `Gallery.html` | Photo gallery with hidden admin upload |
| `Location.html` | Location, hours, map, working contact form (Web3Forms + hCaptcha) |
| `Catering.html` | Catering info page (optional — see "Optional pages & sections") |
| `_nav.html`, `_footer.html`, `_schema_restaurant.html` | Partials injected via `{{> name}}` |
| `css/styles.css` | Shared "Chili Oil & Porcelain" stylesheet for all pages |
| `css/theme.css.tpl` | Generated into `css/theme.css` from `theme.*` at build time |
| `js/gallery.js` | Gallery: public display, admin upload (IndexedDB), admin lock/unlock |
| `js/reveal.js` | Scroll-triggered fade-in animations |
| `js/external-links.js` | Opens off-site links in new tab |

Root asset directories (`gallery-photo/`, `menu-photo/`, `location-photo/`,
`branding-photo/`, `uploads/`) ship with generic `*-placeholder.svg` images
referenced from `media.*` in `config.json`, so a fresh clone builds and runs
without any restaurant-specific photography. One exception: `media.og_image`
should ultimately be a real JPG/PNG (≥1200×630) — social platforms don't
render SVGs in share previews. Photographic slots (hero, gallery, menu,
location, ingredients) work with JPG/PNG/WEBP just as well as SVG — `build.py`
does pure string substitution + file copy and doesn't care about format.

## Optional pages & sections

Not every restaurant needs every section, so `build.py` can drop pieces of the
template entirely based on `config.json`:

- **`restaurant.has_catering`** (`"True"`/`"False"`) — when `"False"`,
  `build.py` deletes `dist/Catering.html` and removes the "Catering" link from
  the nav and footer. Defaults to `"True"` if the key is missing.
- **Instagram section** (homepage) — shown only if `links.instagram` is
  non-empty. Leave it blank (the default in the generic template skeleton) to
  hide the section entirely; no separate flag needed.

Both are implemented with a tiny `{{#if flat.key}}...{{/if}}` block syntax in
`template/*.html` / partials: `build.py` keeps the block's contents if the
named flat config key is truthy (non-empty and not `"false"`/`"no"`/`"0"`/
`"none"`, case-insensitive) and removes the whole block — markers included —
otherwise. Use this same pattern for any other optional page/section driven by
a config flag or link.

## Design system

`template/css/styles.css` defines a "Chili Oil & Porcelain" visual language
via CSS custom properties at `:root`, with brand colors overridden per-site by
the generated `css/theme.css` (driven by `theme.*` in `config.json`):

- **Colors:** `--accent` (lacquer red), `--ember` (chili-oil amber), `--cream` (porcelain background) — default values in the root `config.json`'s `theme.*` match `#be2f25` / `#e89033` / `#f8f2e8`
- **Fonts:** Montserrat (headings/UI) + Open Sans (body), loaded from Google Fonts
- **Shadows/radius:** `--shadow-sm/md/lg`, `--radius`, `--radius-lg`
- Keep all new styles consistent with these tokens rather than adding raw hex values.

## Gallery admin system

- Public gallery is driven by `gallery-photo/photos.json` — add image files + update this JSON to publish to all visitors.
- Admin mode is unlocked via `Gallery.html#admin` or the "Owner login" footer link, using the passcode from `gallery_admin.passcode` in `config.json` (injected into `js/gallery.js` via `GALLERY_CONFIG`).
- Admin uploads are stored in the browser's **IndexedDB only** — they are a local preview and do not publish to other visitors.

## Contact form

`Location.html` uses Web3Forms (no backend needed). Submissions go to the email associated with the Web3Forms access key in `site.web3forms_key`. Generate a key at web3forms.com per restaurant and set it in that site's `config.json`.

## CSS cache-busting

`styles.css` is referenced with a version query string (`?v=2`). Increment this in `template/*.html` when deploying CSS changes so browsers pick up the new file.
