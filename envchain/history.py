"""Track change history for chains (add/update/delete variable events)."""

import json
import os
from datetime import datetime, timezone
from typing import Optional

HISTORY_FILE = os.path.expanduser("~/.envchain_history.json")


def _get_history_path(history_file: str = HISTORY_FILE) -> str:
    return history_file


def _load_history(history_file: str = HISTORY_FILE) -> list:
    path = _get_history_path(history_file)
    if not os.path.exists(path):
        return []
    with open(path, "r") as f:
        return json.load(f)


def _save_history(events: list, history_file: str = HISTORY_FILE) -> None:
    path = _get_history_path(history_file)
    with open(path, "w") as f:
        json.dump(events, f, indent=2)


def record_event(
    chain: str,
    action: str,
    variable: Optional[str] = None,
    note: Optional[str] = None,
    history_file: str = HISTORY_FILE,
) -> dict:
    """Record a history event. action: 'add', 'update', 'delete', 'remove_chain'."""
    event = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "chain": chain,
        "action": action,
        "variable": variable,
        "note": note,
    }
    events = _load_history(history_file)
    events.append(event)
    _save_history(events, history_file)
    return event


def get_history(
    chain: Optional[str] = None,
    action: Optional[str] = None,
    history_file: str = HISTORY_FILE,
) -> list:
    """Return history events, optionally filtered by chain and/or action."""
    events = _load_history(history_file)
    if chain:
        events = [e for e in events if e.get("chain") == chain]
    if action:
        events = [e for e in events if e.get("action") == action]
    return events


def clear_history(chain: Optional[str] = None, history_file: str = HISTORY_FILE) -> int:
    """Clear all history or only for a specific chain. Returns number removed."""
    events = _load_history(history_file)
    if chain:
        kept = [e for e in events if e.get("chain") != chain]
    else:
        kept = []
    removed = len(events) - len(kept)
    _save_history(kept, history_file)
    return removed
