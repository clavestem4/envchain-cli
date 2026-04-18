"""Per-chain access log: track who accessed what and when."""

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

DEFAULT_ACCESS_LOG_DIR = Path.home() / ".envchain" / "access_logs"


def _get_log_path(chain_name: str, base_dir: Optional[Path] = None) -> Path:
    base = base_dir or DEFAULT_ACCESS_LOG_DIR
    base.mkdir(parents=True, exist_ok=True)
    return base / f"{chain_name}.jsonl"


def record_access(chain_name: str, action: str, user: Optional[str] = None, base_dir: Optional[Path] = None) -> None:
    """Append an access entry for the given chain."""
    log_path = _get_log_path(chain_name, base_dir)
    entry = {
        "chain": chain_name,
        "action": action,
        "user": user or os.environ.get("USER", "unknown"),
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    with open(log_path, "a") as f:
        f.write(json.dumps(entry) + "\n")


def get_access_log(chain_name: str, action: Optional[str] = None, base_dir: Optional[Path] = None) -> list:
    """Read access log entries for a chain, optionally filtered by action."""
    log_path = _get_log_path(chain_name, base_dir)
    if not log_path.exists():
        return []
    entries = []
    with open(log_path) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            entry = json.loads(line)
            if action is None or entry.get("action") == action:
                entries.append(entry)
    return entries


def clear_access_log(chain_name: str, base_dir: Optional[Path] = None) -> None:
    """Delete the access log for a chain."""
    log_path = _get_log_path(chain_name, base_dir)
    if log_path.exists():
        log_path.unlink()


def list_accessed_chains(base_dir: Optional[Path] = None) -> list:
    """Return all chain names that have access logs."""
    base = base_dir or DEFAULT_ACCESS_LOG_DIR
    if not base.exists():
        return []
    return [p.stem for p in sorted(base.glob("*.jsonl"))]
