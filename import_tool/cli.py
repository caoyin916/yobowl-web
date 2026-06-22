#!/usr/bin/env python3
"""CLI for the restaurant onboarding import tool.

    python3 -m import_tool.cli import  --url <store-url> --slug <slug>
    python3 -m import_tool.cli fetch   --url <store-url> --slug <slug> [--refetch]
    python3 -m import_tool.cli gapfill --slug <slug> [--url <store-url>]
    python3 -m import_tool.cli merge   --slug <slug> [--dry-run]

Outputs land in onboarding/<slug>/ (gitignored):
    raw_source.html   — cached page fetch (so re-runs don't hit the network)
    menu.json         — full structured menu (sections/items/prices/photos)
    import.json       — draft config + _meta + _field_provenance (merge baseline)
    config.json       — the live, human-editable draft for the new restaurant's repo

See import_tool/README.md for the adapter pattern, the TODO_MANUAL convention,
and how the merge keeps re-imports from clobbering hand edits.
"""
import argparse
import dataclasses
import json
import sys
from pathlib import Path

from import_tool.adapters import get_adapter_for_url
from import_tool.adapters.base import AdapterError
from import_tool.gapfill import build_draft_config
from import_tool.merge import (
    CONFIG_FILENAME, DRAFT_FILENAME, IMPORT_FILENAME,
    build_import_record, format_diff, strip_meta, three_way_merge,
)

DEFAULT_OUT_DIR = "onboarding"
RAW_FILENAME = "raw_source.html"
MENU_FILENAME = "menu.json"


def _out_dir(args):
    out = Path(args.out_dir) / args.slug
    out.mkdir(parents=True, exist_ok=True)
    return out


def _write_json(path, data):
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def _load_json(path):
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else None


def _to_jsonable(value):
    """Dataclasses (and nested dataclasses/dicts/lists) -> plain JSON-able values."""
    if dataclasses.is_dataclass(value):
        return {k: _to_jsonable(v) for k, v in dataclasses.asdict(value).items()}
    if isinstance(value, dict):
        return {k: _to_jsonable(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [_to_jsonable(v) for v in value]
    return value


def _recover_source_url(out_dir, args):
    """`gapfill` can be re-run without --url by recovering it from a cached
    import record — the adapter needs source_url to populate order_online_url
    and to be re-selected via get_adapter_for_url()."""
    if args.url:
        return args.url
    for filename in (DRAFT_FILENAME, IMPORT_FILENAME):
        record = _load_json(out_dir / filename)
        if record:
            url = record.get("_meta", {}).get("source_url")
            if url:
                return url
    return None


def cmd_fetch(args):
    out_dir = _out_dir(args)
    raw_path = out_dir / RAW_FILENAME
    if raw_path.exists() and not args.refetch:
        print(f"Using cached {raw_path} (pass --refetch to re-download)")
        return raw_path.read_text(encoding="utf-8")
    adapter = get_adapter_for_url(args.url, args.platform)
    print(f"Fetching {args.url} via the {adapter.PLATFORM} adapter…")
    raw = adapter.fetch(args.url)
    raw_path.write_text(raw, encoding="utf-8")
    print(f"  -> cached to {raw_path}")
    return raw


def cmd_gapfill(args, data=None):
    out_dir = _out_dir(args)

    if data is None:
        raw_path = out_dir / RAW_FILENAME
        if not raw_path.exists():
            sys.exit(f"ERROR: no cached {raw_path} — run `fetch` or `import` first")
        source_url = _recover_source_url(out_dir, args)
        if not source_url:
            sys.exit("ERROR: --url is required (no cached import record to recover it from)")
        adapter = get_adapter_for_url(source_url, args.platform)
        try:
            data = adapter.parse(raw_path.read_text(encoding="utf-8"), source_url)
        except AdapterError as exc:
            sys.exit(f"ERROR: {exc}")

    if data.menu:
        _write_json(out_dir / MENU_FILENAME, _to_jsonable(data.menu))

    config, provenance = build_draft_config(data, args.slug)
    record = build_import_record(config, provenance)

    config_path = out_dir / CONFIG_FILENAME
    if config_path.exists():
        draft_path = out_dir / DRAFT_FILENAME
        _write_json(draft_path, record)
        print(f"  -> {config_path} already exists; wrote a fresh draft to {draft_path}")
        print(f"     run `python3 -m import_tool.cli merge --slug {args.slug} --dry-run` to preview the merge")
    else:
        _write_json(out_dir / IMPORT_FILENAME, record)
        _write_json(config_path, strip_meta(config))
        print(f"  -> wrote {out_dir / IMPORT_FILENAME} and initial {config_path}")

    return data, config, provenance


def cmd_import(args):
    if not args.url:
        sys.exit("ERROR: --url is required for `import`")
    out_dir = _out_dir(args)
    raw = cmd_fetch(args)
    adapter = get_adapter_for_url(args.url, args.platform)
    try:
        data = adapter.parse(raw, args.url)
    except AdapterError as exc:
        sys.exit(f"ERROR: {exc}")
    _, _, provenance = cmd_gapfill(args, data=data)
    _print_summary(data, provenance, out_dir)


def cmd_merge(args):
    out_dir = _out_dir(args)
    import_path = out_dir / IMPORT_FILENAME
    config_path = out_dir / CONFIG_FILENAME
    draft_path = out_dir / DRAFT_FILENAME

    mine_config = _load_json(config_path)
    draft_record = _load_json(draft_path)
    base_record = _load_json(import_path)

    if mine_config is None:
        sys.exit(f"ERROR: no {config_path} — run `import` first")
    if draft_record is None:
        sys.exit(f"ERROR: no {draft_path} — run `import` again to generate a fresh draft to merge against")
    if base_record is None:
        sys.exit(f"ERROR: no {import_path} baseline found — this shouldn't happen for an "
                 f"onboarding dir created by this tool; re-run `import` into a clean directory")

    theirs_config = strip_meta(draft_record)
    theirs_provenance = draft_record.get("_field_provenance", {})
    merged, diff = three_way_merge(base_record, mine_config, theirs_config, theirs_provenance)

    print(f"Merge plan for {out_dir}:")
    rendered = format_diff(diff)
    print(rendered if rendered else "  (no changes — current config already matches the latest draft)")

    if args.dry_run:
        print("\n(dry run — nothing written; re-run without --dry-run to apply)")
        return

    _write_json(config_path, merged)
    _write_json(import_path, draft_record)
    draft_path.unlink()
    print(f"\n-> wrote {config_path}, refreshed {import_path} as the new baseline, removed {draft_path}")


def _print_summary(data, provenance, out_dir):
    by_kind = {"source": [], "generated": [], "manual": []}
    for path, kind in provenance.items():
        by_kind[kind].append(path)

    menu_note = ""
    if data.menu:
        item_count = sum(len(section.items) for section in data.menu.sections)
        menu_note = (f", {len(data.menu.sections)} menu sections ({item_count} items) "
                     f"-> {out_dir / MENU_FILENAME}")

    print(f"\nSummary for {data.name!r} ({data.source_platform}){menu_note}")
    print(f"  Extracted from source : {len(by_kind['source'])} fields")
    print(f"  Generated/templated   : {len(by_kind['generated'])} fields")
    print(f"  Needs manual input    : {len(by_kind['manual'])} fields")
    if by_kind["manual"]:
        print("    " + ", ".join(sorted(by_kind["manual"])))
    print(f"\nNext: open {out_dir / CONFIG_FILENAME} and resolve every TODO_MANUAL: marker"
          f" (grep -n TODO_MANUAL {out_dir / CONFIG_FILENAME}).")
    print(
        "\nAlso replace these placeholder images with your own restaurant's photos"
        " (they ship as generic *-placeholder.svg files so the template builds out of the box):\n"
        "  gallery-photo/   - public gallery photos (listed in gallery-photo/photos.json)\n"
        "  menu-photo/      - featured menu images + catering menu PDF/image\n"
        "  location-photo/  - storefront / parking-guide photo\n"
        "  branding-photo/  - hero background, logo, social-share image, ingredients photo\n"
        "See import_tool/README.md -> \"What's configurable\" for the full reference\n"
        "(note: media.og_image needs a real JPG/PNG before going live -- "
        "social platforms don't render SVG share previews).\n"
        "theme.* ships with a generic starting palette -- customize the hex values"
        " to match this restaurant's actual branding before launch."
    )


def build_parser():
    parser = argparse.ArgumentParser(
        prog="import_tool.cli",
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    sub = parser.add_subparsers(dest="command", required=True)

    def add_common(p, url_required=False):
        p.add_argument("--slug", required=True, help="onboarding directory name, e.g. show-mian-plano")
        p.add_argument("--url", required=url_required, default=None, help="source platform store URL")
        p.add_argument("--out-dir", default=DEFAULT_OUT_DIR, help=f"output root (default: {DEFAULT_OUT_DIR})")
        p.add_argument("--platform", default=None, help="force a specific adapter (default: auto-detect from --url)")

    p_import = sub.add_parser("import", help="fetch + parse + gap-fill -> onboarding/<slug>/")
    add_common(p_import, url_required=True)
    p_import.add_argument("--refetch", action="store_true", help="re-download even if raw_source.html is cached")
    p_import.set_defaults(func=cmd_import)

    p_fetch = sub.add_parser("fetch", help="download and cache the source page only")
    add_common(p_fetch, url_required=True)
    p_fetch.add_argument("--refetch", action="store_true", help="re-download even if raw_source.html is cached")
    p_fetch.set_defaults(func=cmd_fetch)

    p_gapfill = sub.add_parser("gapfill", help="re-run parsing + gap-fill from the cached page")
    add_common(p_gapfill)
    p_gapfill.set_defaults(func=cmd_gapfill)

    p_merge = sub.add_parser("merge", help="three-way merge a fresh draft into config.json")
    add_common(p_merge)
    p_merge.add_argument("--dry-run", action="store_true", help="print the merge plan without writing anything")
    p_merge.set_defaults(func=cmd_merge)

    return parser


def main(argv=None):
    args = build_parser().parse_args(argv)
    args.func(args)


if __name__ == "__main__":
    main()
