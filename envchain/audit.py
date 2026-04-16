"""Audit log for envchain operations."""

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

DEFAULT_AUDIT_PATH = Path.home() / ".envchain" / "audit.log"


def _get_audit_path() -> Path:
    path = Path(os.environ.get("ENVCHAIN_AUDIT_LOG", DEFAULT_AUDIT_PATH))
    path.parent.mkdir(parents=True, exist_ok=True)
    return path


def log_event(action: str, chain_name: str, detail: Optional[str] = None) -> None:
    """Append a structured audit event to the audit log."""
    event = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "action": action,
        "chain": chain_name,
    }
    if detail:
        event["detail"] = detail

    audit_path = _get_audit_path()
    with audit_path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(event) + "\n")


def read_events(chain_name: Optional[str] = None) -> list[dict]:
    """Read audit events, optionally filtered by chain name."""
    audit_path = _get_audit_path()
    if not audit_path.exists():
        return []

    events = []
    with audit_path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                event = json.loads(line)
                if chain_name is None or event.get("chain") == chain_name:
                    events.append(event)
            except json.JSONDecodeError:
                continue
    return events


def clear_events(chain_name: Optional[str] = None) -> int:
    """Clear audit events. Returns number of removed entries."""
    audit_path = _get_audit_path()
    if not audit_path.exists():
        return 0

    if chain_name is None:
        count = len(read_events())
        audit_path.write_text("", encoding="utf-8")
        return count

    all_events = read_events()
    kept = [e for e in all_events if e.get("chain") != chain_name]
    removed = len(all_events) - len(kept)
    with audit_path.open("w", encoding="utf-8") as f:
        for e in kept:
            f.write(json.dumps(e) + "\n")
    return removed
