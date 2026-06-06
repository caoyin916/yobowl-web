# Restaurant Website Template & Automation Pipeline

## Context

The Yo Bowl Carrollton site is a proven, high-quality static HTML/CSS/JS restaurant website
(~1,300 lines across 6 pages, no build system, no npm). The goal is to transform it into a
reusable master template so new restaurants can be onboarded by filling in one `config.json`
and swapping an assets folder — with Netlify deploying automatically on every git push.

Restaurant-specific data is currently hardcoded 150+ times across all pages (name ×48,
phone ×13, address ×18, hours ×7, social links ×5, order URL ×10, domain ×23). ~70% of each
HTML file is duplicated boilerplate (head meta, nav, footer). The plan below eliminates all
that duplication through a zero-dependency Python build step.

---

## Part 1: MVP Stack (Minimum Viable Pipeline)

### Recommended tools

| Concern | Tool | Why |
|---|---|---|
| Hosting | **Netlify** (free tier) | Auto-deploy on git push, free custom domains, 100 GB/mo bandwidth |
| CI/CD | **Netlify's built-in** | Just set build command to `python3 build.py` |
| Template engine | **Python build script** | Zero dependencies, matches existing "no npm" philosophy |
| Version control | **GitHub** (Template Repos) | One-click repo creation per restaurant |
| Config | **`config.json`** per restaurant | Non-technical-friendly, easy to script against |

### End-to-end workflow for a new restaurant

1. Click **"Use this template"** on the master GitHub repo → creates new restaurant repo
2. Edit `config.json` with restaurant data
3. Drop images into `assets/`
4. `git push` → Netlify auto-runs `python3 build.py` → site is live
5. Configure custom domain in Netlify dashboard (~2 min)

Total human time per new restaurant: **< 30 minutes**

---

## Part 2: Folder Structure

```
restaurant-template/           ← GitHub Template Repo (the master)
│
├── template/                  ← CORE — never edit per-restaurant; pull updates here
│   ├── _head.html             ← Shared <head> partial (meta, OG, schema.org, CSS link)
│   ├── _nav.html              ← Shared nav/header partial
│   ├── _footer.html           ← Shared footer partial
│   ├── index.html             ← Page shell: includes partials + page body with {{PLACEHOLDERS}}
│   ├── Menu.html
│   ├── Gallery.html
│   ├── Location.html
│   ├── Catering.html
│   ├── css/
│   │   ├── styles.css         ← Shared stylesheet (uses CSS vars; theme vars injected at build)
│   │   └── theme.css.tpl      ← Template for generated theme.css (brand colors from config)
│   └── js/
│       ├── gallery.js
│       ├── reveal.js
│       └── external-links.js
│
├── assets/                    ← RESTAURANT-SPECIFIC — swap these per restaurant
│   ├── hero.jpg
│   ├── logo.png
│   ├── og-image.jpg
│   ├── gallery/
│   │   └── photos.json        ← Gallery manifest
│   ├── menu-photo/
│   └── location-photo/
│
├── config.json                ← THE ONE FILE TO FILL OUT
├── build.py                   ← Reads config.json + renders template/ → dist/
├── netlify.toml               ← Build command + publish dir
├── .gitignore                 ← Ignore dist/
└── dist/                      ← Generated output (git-ignored, Netlify serves this)
```

---

## Part 3: `config.json` Schema (Full Example)

```json
{
  "restaurant": {
    "name": "Yo Bowl Carrollton",
    "name_short": "Yo Bowl",
    "initials": "YB",
    "tagline": "Authentic Chinese Mifen & Dumplings",
    "description": "Authentic Chinese comfort food in Carrollton, TX — Braised Beef Mifen, Signature Dry Mifen, Fresh Yogurt & Dumplings, made fresh.",
    "cuisine": ["Chinese", "Asian", "Noodles"],
    "price_range": "$$",
    "copyright_year": "2026"
  },
  "contact": {
    "phone_display": "(469) 892-6267",
    "phone_e164": "+1-469-892-6267",
    "phone_tel": "+14698926267",
    "email": "contact@yobowlcarrollton.com",
    "address": {
      "street": "2700 Old Denton Rd Unit 110",
      "city": "Carrollton",
      "state": "TX",
      "zip": "75007",
      "country": "US",
      "landmark": "next to Young Sook Lee CPA"
    },
    "coordinates": {
      "lat": 32.9898,
      "lng": -96.9075
    }
  },
  "hours": {
    "schema_opens": "11:00",
    "schema_closes": "21:00",
    "days_of_week": ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"],
    "display": "Mon – Sun  11:00 AM – 9:00 PM",
    "carryout_display": "Mon – Sun  11:00 AM – 8:30 PM"
  },
  "site": {
    "domain": "yobowlcarrollton.com",
    "base_url": "https://www.yobowlcarrollton.com",
    "web3forms_key": "YOUR_KEY_HERE"
  },
  "links": {
    "order_online": "https://order.toasttab.com/online/yobowl",
    "instagram": "https://www.instagram.com/yobowl.carrollton/",
    "instagram_handle": "@yobowl.carrollton",
    "maps": "https://maps.google.com/?q=2700+Old+Denton+Rd+Unit+110+Carrollton+TX+75007"
  },
  "media": {
    "hero_image": "assets/hero.jpg",
    "logo": "assets/logo.png",
    "og_image": "assets/og-image.jpg"
  },
  "theme": {
    "accent": "#be2f25",
    "accent_dark": "#8c1c14",
    "ember": "#e89033",
    "gold": "#d6a437",
    "cream": "#f8f2e8",
    "cream_deep": "#f1e8d8",
    "ink": "#211a15",
    "font_head": "Montserrat",
    "font_body": "Open Sans"
  },
  "menu_highlights": [
    "Braised Beef Mifen",
    "Signature Dry Mifen",
    "Fresh Yogurt",
    "Dumplings"
  ]
}
```

---

## Part 4: Template Injection — `build.py`

### Placeholder syntax in HTML templates

Use `{{KEY}}` for simple string replacement with dot notation for nested keys:

```html
<!-- template/index.html (head excerpt) -->
<title>{{restaurant.name}} | {{restaurant.tagline}}</title>
<meta name="description" content="{{restaurant.description}}">
<meta property="og:url" content="{{site.base_url}}/">
<link rel="canonical" href="{{site.base_url}}/">
<link rel="stylesheet" href="css/styles.css?v=2">
<link rel="stylesheet" href="css/theme.css">
```

```html
<!-- footer partial: template/_footer.html -->
<footer>
  <p class="brand">{{restaurant.name_short}}<small>{{contact.address.city}}</small></p>
  <p>{{contact.address.street}}, {{contact.address.city}}, {{contact.address.state}} {{contact.address.zip}}</p>
  <p><a href="tel:{{contact.phone_tel}}">{{contact.phone_display}}</a></p>
  <p>{{hours.display}}</p>
  <p>© {{restaurant.copyright_year}} {{restaurant.name}}. All rights reserved.</p>
</footer>
```

### `build.py` — zero-dependency Python 3

```python
import json, os, re, shutil
from pathlib import Path

CONFIG = json.loads(Path("config.json").read_text())
TEMPLATE_DIR = Path("template")
DIST_DIR = Path("dist")

def flatten(d, prefix=""):
    out = {}
    for k, v in d.items():
        key = f"{prefix}.{k}" if prefix else k
        if isinstance(v, dict):
            out.update(flatten(v, key))
        elif isinstance(v, list):
            out[key] = ", ".join(str(i) for i in v)
        else:
            out[key] = str(v)
    return out

def inject(text, flat):
    return re.sub(r"\{\{([\w.]+)\}\}", lambda m: flat.get(m.group(1), m.group(0)), text)

def load_partial(name):
    return TEMPLATE_DIR.joinpath(name).read_text()

def render_page(html, flat):
    html = html.replace("{{> head}}", load_partial("_head.html"))
    html = html.replace("{{> nav}}", load_partial("_nav.html"))
    html = html.replace("{{> footer}}", load_partial("_footer.html"))
    return inject(html, flat)

def generate_theme_css(flat):
    tpl = TEMPLATE_DIR.joinpath("css/theme.css.tpl").read_text()
    return inject(tpl, flat)

if DIST_DIR.exists():
    shutil.rmtree(DIST_DIR)
shutil.copytree(TEMPLATE_DIR, DIST_DIR)
shutil.copytree("assets", DIST_DIR / "assets", dirs_exist_ok=True)

flat = flatten(CONFIG)

for html_file in DIST_DIR.glob("*.html"):
    if html_file.name.startswith("_"):
        html_file.unlink()
        continue
    html_file.write_text(render_page(html_file.read_text(), flat))

(DIST_DIR / "css" / "theme.css").write_text(generate_theme_css(flat))
print(f"Build complete → {DIST_DIR}/")
```

### `template/css/theme.css.tpl`

```css
/* Auto-generated from config.json — do not edit */
:root {
  --accent:      {{theme.accent}};
  --accent-dark: {{theme.accent_dark}};
  --ember:       {{theme.ember}};
  --gold:        {{theme.gold}};
  --cream:       {{theme.cream}};
  --cream-deep:  {{theme.cream_deep}};
  --ink:         {{theme.ink}};
  --font-head:   '{{theme.font_head}}', system-ui, sans-serif;
  --font-body:   '{{theme.font_body}}', system-ui, sans-serif;
}
```

The `theme.css` loads after `styles.css`, overriding only the custom properties.
The base `styles.css` needs no placeholders and can be updated from master cleanly.

---

## Part 5: Netlify Setup

### `netlify.toml`

```toml
[build]
  command   = "python3 build.py"
  publish   = "dist"

[build.environment]
  PYTHON_VERSION = "3.11"
```

### Per-restaurant setup (one-time, ~5 min)

1. Connect repo to Netlify → "New site from Git"
2. Build command auto-populated from `netlify.toml`
3. Add custom domain under Site Settings → Domain Management
4. Netlify provisions SSL automatically

---

## Part 6: Git Workflow

### Creating a new restaurant repo

```bash
# On GitHub: click "Use this template" on master-restaurant-template
git clone https://github.com/yourorg/new-restaurant-name
cd new-restaurant-name
# Fill in config.json, drop assets in assets/
git add config.json assets/
git commit -m "Configure Tony's Pizza"
git push   # Netlify auto-deploys
```

### Pulling global template updates

```bash
# One-time setup per restaurant repo (do at creation time)
git remote add template https://github.com/yourorg/master-restaurant-template

# When a template update is released:
git fetch template
git checkout template/main -- template/ build.py netlify.toml
git commit -m "Pull template update v1.3"
git push
```

This merges only `template/`, `build.py`, and `netlify.toml` — never touches
`config.json` or `assets/`.

### Mass-update script (100+ sites)

```bash
#!/bin/bash
REPOS=("~/sites/yobowl-carrollton" "~/sites/tonys-pizza")
for repo in "${REPOS[@]}"; do
  cd "$repo"
  git fetch template
  git checkout template/main -- template/ build.py netlify.toml
  git commit -m "Pull template update $(date +%Y-%m-%d)"
  git push
done
```

---

## Part 7: Edge Cases & Bottlenecks at 100+ Sites

| Issue | Mitigation |
|---|---|
| Pages vary per restaurant (no catering page) | Add `pages` array to config; build.py skips unlisted pages |
| Hour schedules differ (closed Mondays, split shifts) | Use `schedule: [{days, open, close}]` array; build.py formats all representations |
| Different ordering/social platforms | `links` is open-ended; unused keys ignored; social as `[{platform, url}]` array for dynamic rendering |
| Netlify free tier: 300 build min/month | Upgrade to Pro at ~30 sites; or use CloudFlare Pages (unlimited free builds) |
| Config.json schema evolves, old repos miss new keys | `build.py` validates required keys at build time; optional keys get defaults |
| Menu structure unique per restaurant | v1: keep menu HTML hand-authored; v2: add `menu_items` array to config |
| Domain setup is manual | Automate with Netlify CLI (`netlify sites:create`, `netlify domains:add`) |

---

## Part 8: Migration Steps (This Repo → Template)

### Step-by-step execution order

1. **Restructure files**
   - Create `template/` directory; move all `.html`, `css/`, `js/` into it
   - Move `gallery-photo/`, `location-photo/`, `menu-photo/` → `assets/`
   - Create `gallery-photo/` symlink or update paths in config

2. **Extract shared partials** from the duplicated boilerplate across 6 HTML files
   - `template/_head.html` — all `<head>` meta/OG/schema content with `{{PLACEHOLDERS}}`
   - `template/_nav.html` — shared `<header>` / `<nav>`
   - `template/_footer.html` — shared `<footer>`

3. **Replace all hardcoded strings** with `{{KEY}}` placeholders using the config schema
   - ~150 replacements: name, phone, address, hours, URLs, colors

4. **Write `config.json`** populated with Yo Bowl's current data

5. **Add `build.py`** and **`netlify.toml`**

6. **Create `template/css/theme.css.tpl`**; remove hardcoded color vars from `styles.css`

7. **Update `css/styles.css`** to reference `theme.css` for custom property overrides

8. **Test locally**:
   ```bash
   python3 build.py
   python3 -m http.server 8080 --directory dist
   # Open http://localhost:8080/index.html
   grep -r "{{" dist/  # should return nothing
   ```

9. **Mark the GitHub repo as a Template** (Settings → check "Template repository")

---

## Verification

```bash
python3 build.py
python3 -m http.server 8080 --directory dist
# Verify all 5 pages render correctly with Yo Bowl data

grep -r "{{" dist/ && echo "WARN: unreplaced placeholders" || echo "OK: no open placeholders"

# Simulate a second restaurant: change a few config.json values, rebuild, verify changes propagate
```
