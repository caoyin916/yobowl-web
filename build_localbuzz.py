#!/usr/bin/env python3
"""
Sync shared template assets into localbuzz/ so it stays self-contained.

localbuzz/ is deployed directly to Hostinger — it must not reference
../template/ since Hostinger sets the document root to the localbuzz/ folder.
Run this whenever template/css/styles.css, reveal.js, or external-links.js change.

Usage:
    python3 build_localbuzz.py
"""
import shutil
from pathlib import Path

ROOT         = Path(__file__).parent
TEMPLATE_JS  = ROOT / "template" / "js"
TEMPLATE_CSS = ROOT / "template" / "css"
DEST_CSS     = ROOT / "localbuzz" / "css"
DEST_JS      = ROOT / "localbuzz" / "js"

def sync():
    DEST_CSS.mkdir(parents=True, exist_ok=True)
    DEST_JS.mkdir(parents=True, exist_ok=True)

    shutil.copy(TEMPLATE_CSS / "styles.css",        DEST_CSS / "styles.css")
    shutil.copy(TEMPLATE_JS  / "reveal.js",         DEST_JS  / "reveal.js")
    shutil.copy(TEMPLATE_JS  / "external-links.js", DEST_JS  / "external-links.js")

    print("Synced shared template assets into localbuzz/:")
    print("  localbuzz/css/styles.css")
    print("  localbuzz/js/reveal.js")
    print("  localbuzz/js/external-links.js")
    print()
    print("Commit these files along with any changes to localbuzz/index.html or CSS.")

if __name__ == "__main__":
    sync()
