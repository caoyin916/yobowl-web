#!/usr/bin/env python3
"""
Build the Local Buzz Marketing landing page into a self-contained dist/.

Usage:
    python3 build_localbuzz.py

Output:
    localbuzz/dist/  — fully self-contained static site ready to deploy.
                       Upload the contents of this folder to Hostinger's
                       public_html/ (or whatever your document root is).
"""
import re, shutil
from pathlib import Path

ROOT        = Path(__file__).parent
SRC         = ROOT / "localbuzz"
TEMPLATE_JS = ROOT / "template" / "js"
TEMPLATE_CSS= ROOT / "template" / "css"
DIST        = SRC / "dist"

def build():
    # ── Clean and recreate dist/ ─────────────────────────────────────────────
    if DIST.exists():
        shutil.rmtree(DIST)
    DIST.mkdir()
    (DIST / "css").mkdir()
    (DIST / "js").mkdir()

    # ── Copy page-specific CSS ───────────────────────────────────────────────
    shutil.copy(SRC / "css" / "theme.css",   DIST / "css" / "theme.css")
    shutil.copy(SRC / "css" / "landing.css", DIST / "css" / "landing.css")

    # ── Copy shared template assets ──────────────────────────────────────────
    shutil.copy(TEMPLATE_CSS / "styles.css",        DIST / "css" / "styles.css")
    shutil.copy(TEMPLATE_JS  / "reveal.js",         DIST / "js"  / "reveal.js")
    shutil.copy(TEMPLATE_JS  / "external-links.js", DIST / "js"  / "external-links.js")

    # ── Process index.html — rewrite ../template/... paths ───────────────────
    html = (SRC / "index.html").read_text(encoding="utf-8")

    html = html.replace("../template/css/styles.css?v=2", "css/styles.css?v=2")
    html = html.replace("../template/js/reveal.js?v=1",   "js/reveal.js?v=1")
    html = html.replace("../template/js/external-links.js?v=2", "js/external-links.js?v=2")

    (DIST / "index.html").write_text(html, encoding="utf-8")

    print("Built localbuzz/dist/")
    print("  css/styles.css")
    print("  css/theme.css")
    print("  css/landing.css")
    print("  js/reveal.js")
    print("  js/external-links.js")
    print("  index.html")
    print()
    print("To preview locally:")
    print("  cd localbuzz/dist && python3 -m http.server 8099")
    print("  open http://localhost:8099")
    print()
    print("To deploy to Hostinger:")
    print("  Upload the contents of localbuzz/dist/ to public_html/ via")
    print("  Hostinger File Manager or FTP.")

if __name__ == "__main__":
    build()
