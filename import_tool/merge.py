"""import.json <-> config.json bookkeeping: the on-disk record shape and the
three-way merge that makes re-imports safe to run without clobbering hand
edits. See the plan / import_tool/README.md for the full rationale.

On-disk shapes (all live under onboarding/<slug>/):
  import.json        — the most recent accepted draft: full config dict plus
                        "_meta" (source/fetch info) and "_field_provenance"
                        (dot-path -> "source"/"generated"/"manual"). Doubles
                        as the merge baseline ("base") for the next re-import.
  import.draft.json  — a freshly generated draft awaiting `merge` (only
                        present between `import` and `merge` on a re-run).
  config.json        — the live, human-editable draft for the new
                        restaurant's eventual repo ("mine"). No "_meta" /
                        "_field_provenance" — just the plain config shape.
"""
import copy
import json

IMPORT_FILENAME = "import.json"
DRAFT_FILENAME = "import.draft.json"
CONFIG_FILENAME = "config.json"

_MISSING = object()


def strip_meta(config):
    return {k: v for k, v in config.items() if not k.startswith("_")}


def build_import_record(config, provenance):
    record = dict(config)
    record["_field_provenance"] = provenance
    return record


def _get_path(d, path):
    node = d
    for part in path.split("."):
        if not isinstance(node, dict) or part not in node:
            return _MISSING
        node = node[part]
    return node


def _set_path(d, path, value):
    parts = path.split(".")
    node = d
    for part in parts[:-1]:
        node = node.setdefault(part, {})
    node[parts[-1]] = value


def three_way_merge(base_record, mine_config, theirs_config, theirs_provenance):
    """base = previous import.json (last accepted baseline), mine = current
    config.json (possibly hand-edited since), theirs = freshly generated draft.

    Per field:
      - new in theirs, absent from mine  -> ADDED      (take theirs)
      - mine differs from base           -> KEPT       (human edited it; don't touch)
      - mine == base, theirs != base     -> UPDATED    (safe to take the new value)
      - mine == base == theirs           -> unchanged

    Returns (merged_config, diff) where diff is an ordered list of
    (path, old, new, action) tuples — the basis for both --dry-run output
    and the applied merge.
    """
    base_config = strip_meta(base_record)
    base_provenance = base_record.get("_field_provenance", {})
    merged = copy.deepcopy(mine_config)
    diff = []
    for path in sorted(set(base_provenance) | set(theirs_provenance)):
        base_val = _get_path(base_config, path)
        mine_val = _get_path(mine_config, path)
        theirs_val = _get_path(theirs_config, path)
        if theirs_val is _MISSING:
            continue
        if mine_val is _MISSING:
            _set_path(merged, path, theirs_val)
            diff.append((path, None, theirs_val, "ADDED"))
        elif base_val is _MISSING or mine_val != base_val:
            diff.append((path, mine_val, mine_val, "KEPT"))
        elif theirs_val != base_val:
            _set_path(merged, path, theirs_val)
            diff.append((path, mine_val, theirs_val, "UPDATED"))
        else:
            diff.append((path, mine_val, mine_val, "unchanged"))
    return merged, diff


def format_diff(diff, show_unchanged=False):
    lines = []
    for path, old, new, action in diff:
        if action == "unchanged":
            if show_unchanged:
                lines.append(f"  [-]       {path}: {_short(old)}")
            continue
        if action == "ADDED":
            lines.append(f"  [ADDED]   {path}: {_short(new)}")
        elif action == "UPDATED":
            lines.append(f"  [UPDATED] {path}: {_short(old)} -> {_short(new)}")
        elif action == "KEPT":
            lines.append(f"  [KEPT]    {path}: {_short(old)}  (hand-edited — not overwritten)")
    return "\n".join(lines)


def _short(value, limit=80):
    text = value if isinstance(value, str) else json.dumps(value, ensure_ascii=False)
    return text if len(text) <= limit else text[:limit - 1] + "…"
