# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this project is

A static multi-page restaurant website for **Yo Bowl Carrollton** (authentic Chinese mifen & dumplings, Carrollton TX). No build system, no framework, no npm — just HTML, CSS, and vanilla JS files served directly.

Live site: `https://www.yobowlcarrollton.com/`

## Running locally

Open any `.html` file directly in a browser, or serve with any static file server:

```bash
# Run from the repo root
python3 -m http.server 8080
# then open http://localhost:8080/index.html
# (favicon.ico 404 in the server log is harmless)
```

No build step, no compilation, no dependencies to install.

## File map

| File | Purpose |
|------|---------|
| `index.html` | Home page |
| `Menu.html` | Menu page |
| `Gallery.html` | Photo gallery with hidden admin upload |
| `Location.html` | Location, hours, map, working contact form (Web3Forms + hCaptcha) |
| `Catering.html` | Catering info page |
| `css/styles.css` | Single shared stylesheet for all pages |
| `js/gallery.js` | Gallery: public display, admin upload (IndexedDB), admin lock/unlock |
| `js/reveal.js` | Scroll-triggered fade-in animations |
| `js/external-links.js` | Opens off-site links in new tab |
| `image-slot.js` | Standalone utility for owner-managed image slots |
| `gallery-photo/photos.json` | Source-of-truth list of public gallery images |
| `gallery-photo/*.jpg` | Public gallery images |
| `menu-photo/` | Menu images |
| `location-photo/` | Storefront / parking photos |
| `uploads/` | Owner-uploaded assets (not referenced by public pages) |

## Design system

All pages share `css/styles.css` which defines a "Chili Oil & Porcelain" visual language via CSS custom properties at `:root`:

- **Colors:** `--accent` (#be2f25 lacquer red), `--ember` (#e89033 chili-oil amber), `--cream` (#f8f2e8 porcelain background)
- **Fonts:** Montserrat (headings/UI) + Open Sans (body), loaded from Google Fonts
- **Shadows/radius:** `--shadow-sm/md/lg`, `--radius`, `--radius-lg`
- Keep all new styles consistent with these tokens rather than adding raw hex values.

## Gallery admin system

- Public gallery is driven by `gallery-photo/photos.json` — add image files + update this JSON to publish to all visitors.
- Admin mode is unlocked via `Gallery.html#admin` or the "Owner login" footer link, passcode: `yobowl` (configurable in `js/gallery.js` → `ADMIN_PASSCODE`).
- Admin uploads are stored in the browser's **IndexedDB only** — they are a local preview and do not publish to other visitors.

## Contact form

`Location.html` uses Web3Forms (no backend needed). Submissions go to the email associated with the Web3Forms access key in the `name="access_key"` hidden input. To change the destination email, generate a new key at web3forms.com and update that value.

## CSS cache-busting

`styles.css` is referenced with a version query string (`?v=2`). Increment this when deploying CSS changes so browsers pick up the new file.
