# Local Buzz Marketing landing page

The marketing/sales site for **Local Buzz Marketing** — the all-in-one platform
(website + online ordering + AI social media + AI Google review management)
sold to the restaurants whose sites are built from this repo.

This is a **standalone, single-page static site** — separate from the
`build.py` / `config.json` / `sites/<slug>` pipeline (that pipeline is for
per-restaurant client sites; this is the company's own marketing site, so
there's only one "config").

It reuses the shared design system and scripts from `../template/` (fonts,
buttons, section/feature/review layouts, scroll-reveal animation, external
link handling) via relative paths, with its own theme (`css/theme.css`) and
page-specific styles (`css/landing.css`).

## Files

| Path | Purpose |
|---|---|
| `index.html` | The full landing page (header, hero, features, sample sites, FAQ, demo form, footer) |
| `css/theme.css` | Local Buzz Marketing brand palette (violet/amber) — overrides the "Chili Oil & Porcelain" tokens from `../template/css/styles.css` |
| `css/landing.css` | Page-specific layout/styles (hero mockups, pillar grid, comparison table, FAQ accordion, etc.) |

## Running locally

Must be served from the **repo root** (not from inside `buzzai/`), since
`index.html` references `../template/css/styles.css`, `../template/js/reveal.js`,
and `../template/js/external-links.js`:

```bash
cd /Users/kedi/Documents/GitHub/yobowl-web
python3 -m http.server 8099 --directory .
# then open http://localhost:8099/buzzai/index.html
```

## Before going live

- **Web3Forms key** — the demo-request form's `access_key` is still
  `REPLACE_WITH_YOUR_WEB3FORMS_KEY`. Generate a real key at web3forms.com.
- **Sample Restaurant Sites** — currently showcases Yo Bowl (`yobowl.com`).
  Update this list as new client sites launch.
- **Deploying** — same static-hosting approach as the restaurant sites
  (e.g. Netlify). Since this page depends on `../template/`, either deploy
  from the repo root with `buzzai/` as the published subdirectory, or copy
  the referenced `template/css/styles.css`, `template/js/reveal.js`, and
  `template/js/external-links.js` into this folder and update the paths
  before publishing as its own site.
