#!/usr/bin/env python3
"""
Build script: renders template/ + config.json → dist/

Usage:
    python3 build.py                        # build this repo's own root config.json → dist/
    python3 build.py --site <slug>           # build sites/<slug>/config.json → sites/<slug>/dist/

Output:
    dist/  — complete static site ready to serve or deploy
"""
import argparse, json, re, shutil, sys
from pathlib import Path

TEMPLATE_DIR = Path("template")

# Asset directories copied into dist/ (relative to the site root — repo root,
# or sites/<slug>/ when --site is given)
ASSET_DIRS = ["gallery-photo", "menu-photo", "location-photo", "branding-photo", "uploads"]


def load_config(config_file):
    if not config_file.exists():
        sys.exit(f"ERROR: {config_file} not found. Copy the root config.json (the generic "
                 f"template skeleton) to {config_file} and fill it in.")
    return json.loads(config_file.read_text(encoding="utf-8"))


def flatten(d, prefix=""):
    """Flatten nested dict to dot-notation keys: {'a': {'b': 1}} → {'a.b': '1'}"""
    out = {}
    for k, v in d.items():
        key = f"{prefix}.{k}" if prefix else k
        if isinstance(v, dict):
            out.update(flatten(v, key))
        elif isinstance(v, list):
            for idx, item in enumerate(v):
                if isinstance(item, dict):
                    out.update(flatten(item, f"{key}.{idx}"))
                else:
                    out[f"{key}.{idx}"] = str(item)
            out[key] = ", ".join(str(i) for i in v if not isinstance(i, dict))
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


FALSY = {"", "false", "no", "0", "none"}


def strip_conditionals(text, flat):
    """Resolve {{#if flat.key}}...{{/if}} blocks: keep the body if the flat
    config value is truthy, otherwise remove the whole block (used for
    optional sections/links like Instagram and Catering)."""
    def repl(m):
        flag, body = m.group(1), m.group(2)
        value = flat.get(flag, "").strip().lower()
        return "" if value in FALSY else body
    return re.sub(r"\{\{#if ([\w.]+)\}\}(.*?)\{\{/if\}\}", repl, text, flags=re.DOTALL)


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
    html = strip_conditionals(html, page_flat)
    html = inject(html, page_flat)
    return inject(html, page_flat)  # second pass resolves tokens-within-config-values


def build(site_dir=Path(".")):
    config_file = site_dir / "config.json"
    dist_dir    = site_dir / "dist"

    config = load_config(config_file)
    flat   = flatten(config)

    # Auto-generate *_tags_html keys from any *_tags string values
    tags_html = {}
    for k, v in list(flat.items()):
        if k.endswith('.tags') or k.endswith('_tags'):
            spans = "".join(
                f'<span class="tag">{t.strip()}</span>'
                for t in v.split(',') if t.strip()
            )
            tags_html[k + '_html'] = spans
    flat.update(tags_html)

    # Validate required keys
    required = [
        "restaurant.name", "contact.phone_display", "contact.address_city",
        "site.base_url", "links.order_online", "media.hero_bg",
    ]
    missing = [k for k in required if k not in flat]
    if missing:
        sys.exit(f"ERROR: Missing required config keys: {', '.join(missing)}")

    # Clean and recreate dist/
    if dist_dir.exists():
        shutil.rmtree(dist_dir)
    shutil.copytree(TEMPLATE_DIR, dist_dir)

    # Copy asset directories (root's generic placeholders first as a fallback
    # baseline, then the site dir on top so restaurant-specific files of the
    # same name win)
    for asset_dir in ASSET_DIRS:
        for root in (Path("."), site_dir):
            src = root / asset_dir
            if src.exists():
                shutil.copytree(src, dist_dir / asset_dir, dirs_exist_ok=True)

    # Render all HTML pages
    for html_file in list(dist_dir.glob("*.html")):
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
    for partial in dist_dir.glob("_*.html"):
        partial.unlink()

    # Drop the Catering page entirely for restaurants that don't cater
    if flat.get("restaurant.has_catering", "True").strip().lower() in FALSY:
        catering = dist_dir / "Catering.html"
        if catering.exists():
            catering.unlink()

    # Generate theme.css from template
    tpl_path = dist_dir / "css" / "theme.css.tpl"
    if tpl_path.exists():
        css_out = inject(tpl_path.read_text(encoding="utf-8"), flat)
        (dist_dir / "css" / "theme.css").write_text(css_out, encoding="utf-8")
        tpl_path.unlink()

    # Validate: warn about any unreplaced placeholders
    unreplaced = []
    for html_file in dist_dir.glob("*.html"):
        matches = re.findall(r"\{\{[\w.]+\}\}", html_file.read_text(encoding="utf-8"))
        if matches:
            unreplaced.append(f"  {html_file.name}: {', '.join(set(matches))}")
    if unreplaced:
        print("WARN: Unreplaced placeholders found:")
        print("\n".join(unreplaced))
    else:
        print(f"✓ Build complete → {dist_dir}/  (no unreplaced placeholders)")


def main():
    parser = argparse.ArgumentParser(description="Render template/ + config.json → dist/")
    parser.add_argument("--site", metavar="SLUG",
                        help="build sites/<slug>/config.json -> sites/<slug>/dist/ "
                             "instead of this repo's own root config.json -> dist/")
    args = parser.parse_args()

    site_dir = Path("sites") / args.site if args.site else Path(".")
    if args.site and not (site_dir / "config.json").exists():
        sys.exit(f"ERROR: {site_dir / 'config.json'} not found — "
                 f"create sites/{args.site}/config.json first")
    build(site_dir)


if __name__ == "__main__":
    main()
