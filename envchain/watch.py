"""Watch chains for variable changes and report drift."""
from typing import Optional
from envchain.chain import get_chain, get_chain_names


def snapshot_chain(chain_name: str, password: str) -> dict:
    """Return a snapshot of current chain variables."""
    chain = get_chain(chain_name, password)
    return dict(chain)


def detect_drift(chain_name: str, password: str, baseline: dict) -> dict:
    """Compare current chain state to a baseline snapshot.

    Returns a dict with keys: added, removed, modified.
    """
    current = snapshot_chain(chain_name, password)
    baseline_keys = set(baseline.keys())
    current_keys = set(current.keys())

    added = {k: current[k] for k in current_keys - baseline_keys}
    removed = {k: baseline[k] for k in baseline_keys - current_keys}
    modified = {
        k: {"before": baseline[k], "after": current[k]}
        for k in baseline_keys & current_keys
        if baseline[k] != current[k]
    }

    return {"added": added, "removed": removed, "modified": modified}


def has_drift(drift: dict) -> bool:
    """Return True if any drift was detected."""
    return bool(drift["added"] or drift["removed"] or drift["modified"])


def format_drift_report(chain_name: str, drift: dict) -> str:
    """Format drift report as human-readable string."""
    if not has_drift(drift):
        return f"[{chain_name}] No drift detected."

    lines = [f"[{chain_name}] Drift detected:"]
    for k, v in drift["added"].items():
        lines.append(f"  + {k}={v}")
    for k, v in drift["removed"].items():
        lines.append(f"  - {k}={v}")
    for k, info in drift["modified"].items():
        lines.append(f"  ~ {k}: '{info['before']}' -> '{info['after']}'")
    return "\n".join(lines)
