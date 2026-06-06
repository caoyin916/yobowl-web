#!/usr/bin/env python3
"""
Build script: renders template/ + config.json → dist/

Usage:
    python3 build.py

Output:
    dist/  — complete static site ready to serve or deploy
"""
import json, re, shutil, sys
from pathlib import Path

TEMPLATE_DIR = Path("template")
DIST_DIR     = Path("dist")
CONFIG_FILE  = Path("config.json")

# Asset directories to copy into dist/ (relative to repo root)
ASSET_DIRS = ["gallery-photo", "menu-photo", "location-photo", "uploads"]


def load_config():
    if not CONFIG_FILE.exists():
        sys.exit(f"ERROR: {CONFIG_FILE} not found. Copy config.json.example and fill it in.")
    return json.loads(CONFIG_FILE.read_text(encoding="utf-8"))


def flatten(d, prefix=""):
    """Flatten nested dict to dot-notation keys: {'a': {'b': 1}} → {'a.b': '1'}"""
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
    """Replace all {{KEY}} placeholders with values from flat config dict."""
    return re.sub(
        r"\{\{([\w.]+)\}\}",
        lambda m: flat.get(m.group(1), m.group(0)),
        text
    )


def load_partial(name):
    path = TEMPLATE_DIR / name
    if not path.exists():
        sys.exit(f"ERROR: Partial not found: {path}")
    return path.read_text(encoding="utf-8")


def render_page(html, flat, page_name=""):
    """Inject partials first, then replace all placeholders."""
    # Build a page-local flat dict so page_file resolves correctly per page
    page_flat = dict(flat)
    page_flat["page_file"] = page_name
    html = html.replace("{{> nav}}", load_partial("_nav.html"))
    html = html.replace("{{> footer}}", load_partial("_footer.html"))
    # Schema partial — strip any arguments from {{> schema_restaurant ...}} syntax
    html = re.sub(
        r"\{\{> schema_restaurant[^}]*\}\}",
        load_partial("_schema_restaurant.html"),
        html
    )
    return inject(html, page_flat)


def build():
    config = load_config()
    flat   = flatten(config)

    # Validate required keys
    required = [
        "restaurant.name", "contact.phone_display", "contact.address_city",
        "site.base_url", "links.order_online", "media.hero_bg",
    ]
    missing = [k for k in required if k not in flat]
    if missing:
        sys.exit(f"ERROR: Missing required config keys: {', '.join(missing)}")

    # Clean and recreate dist/
    if DIST_DIR.exists():
        shutil.rmtree(DIST_DIR)
    shutil.copytree(TEMPLATE_DIR, DIST_DIR)

    # Copy asset directories
    for asset_dir in ASSET_DIRS:
        src = Path(asset_dir)
        if src.exists():
            shutil.copytree(src, DIST_DIR / asset_dir, dirs_exist_ok=True)

    # Render all HTML pages
    for html_file in list(DIST_DIR.glob("*.html")):
        if html_file.name.startswith("_"):
            html_file.unlink()  # remove partial files from output
            continue
        # index.html has no filename in its canonical URL (uses trailing slash)
        page_name = "" if html_file.name == "index.html" else html_file.name
        html_file.write_text(
            render_page(html_file.read_text(encoding="utf-8"), flat, page_name),
            encoding="utf-8"
        )

    # Remove remaining partial files (e.g. _schema_restaurant.html)
    for partial in DIST_DIR.glob("_*.html"):
        partial.unlink()

    # Generate theme.css from template
    tpl_path = DIST_DIR / "css" / "theme.css.tpl"
    if tpl_path.exists():
        css_out = inject(tpl_path.read_text(encoding="utf-8"), flat)
        (DIST_DIR / "css" / "theme.css").write_text(css_out, encoding="utf-8")
        tpl_path.unlink()

    # Validate: warn about any unreplaced placeholders
    unreplaced = []
    for html_file in DIST_DIR.glob("*.html"):
        matches = re.findall(r"\{\{[\w.]+\}\}", html_file.read_text(encoding="utf-8"))
        if matches:
            unreplaced.append(f"  {html_file.name}: {', '.join(set(matches))}")
    if unreplaced:
        print("WARN: Unreplaced placeholders found:")
        print("\n".join(unreplaced))
    else:
        print(f"✓ Build complete → {DIST_DIR}/  (no unreplaced placeholders)")


if __name__ == "__main__":
    build()
