"""Snapshot feature: save and restore named snapshots of a chain's variables."""

import json
import os
from datetime import datetime, timezone
from typing import Optional

SNAPSHOT_DIR = os.path.expanduser("~/.envchain/snapshots")


def _snapshot_path(chain_name: str, snapshot_name: str) -> str:
    return os.path.join(SNAPSHOT_DIR, chain_name, f"{snapshot_name}.json")


def save_snapshot(chain_name: str, variables: dict, snapshot_name: Optional[str] = None) -> str:
    """Save a snapshot of the given variables for a chain. Returns snapshot name."""
    if snapshot_name is None:
        snapshot_name = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    path = _snapshot_path(chain_name, snapshot_name)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    data = {
        "chain": chain_name,
        "snapshot": snapshot_name,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "variables": variables,
    }
    with open(path, "w") as f:
        json.dump(data, f, indent=2)
    return snapshot_name


def load_snapshot(chain_name: str, snapshot_name: str) -> dict:
    """Load a snapshot and return its variables."""
    path = _snapshot_path(chain_name, snapshot_name)
    if not os.path.exists(path):
        raise FileNotFoundError(f"Snapshot '{snapshot_name}' not found for chain '{chain_name}'.")
    with open(path) as f:
        data = json.load(f)
    return data["variables"]


def list_snapshots(chain_name: str) -> list:
    """Return list of snapshot names for a chain, sorted by name."""
    chain_dir = os.path.join(SNAPSHOT_DIR, chain_name)
    if not os.path.exists(chain_dir):
        return []
    names = [f[:-5] for f in os.listdir(chain_dir) if f.endswith(".json")]
    return sorted(names)


def delete_snapshot(chain_name: str, snapshot_name: str) -> None:
    """Delete a named snapshot."""
    path = _snapshot_path(chain_name, snapshot_name)
    if not os.path.exists(path):
        raise FileNotFoundError(f"Snapshot '{snapshot_name}' not found for chain '{chain_name}'.")
    os.remove(path)
