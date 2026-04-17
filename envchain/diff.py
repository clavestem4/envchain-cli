"""Diff utilities for comparing chain variable sets."""
from typing import Dict, Any


def diff_chains(chain_a: Dict[str, Any], chain_b: Dict[str, Any]) -> Dict[str, Any]:
    """Compare two chain variable dicts and return a structured diff."""
    keys_a = set(chain_a.keys())
    keys_b = set(chain_b.keys())

    added = {k: chain_b[k] for k in keys_b - keys_a}
    removed = {k: chain_a[k] for k in keys_a - keys_b}
    modified = {
        k: {"old": chain_a[k], "new": chain_b[k]}
        for k in keys_a & keys_b
        if chain_a[k] != chain_b[k]
    }
    unchanged = {
        k: chain_a[k]
        for k in keys_a & keys_b
        if chain_a[k] == chain_b[k]
    }

    return {
        "added": added,
        "removed": removed,
        "modified": modified,
        "unchanged": unchanged,
    }


def format_diff(diff: Dict[str, Any], show_values: bool = False) -> str:
    """Format a diff dict as a human-readable string."""
    lines = []

    for key in sorted(diff["added"]):
        val = f" = {diff['added'][key]}" if show_values else ""
        lines.append(f"  + {key}{val}")

    for key in sorted(diff["removed"]):
        val = f" = {diff['removed'][key]}" if show_values else ""
        lines.append(f"  - {key}{val}")

    for key in sorted(diff["modified"]):
        if show_values:
            lines.append(f"  ~ {key}: {diff['modified'][key]['old']} -> {diff['modified'][key]['new']}")
        else:
            lines.append(f"  ~ {key}")

    for key in sorted(diff["unchanged"]):
        lines.append(f"    {key}")

    return "\n".join(lines) if lines else "  (no variables)"
