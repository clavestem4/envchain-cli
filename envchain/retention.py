"""Retention policy management for envchain chains."""

from datetime import datetime, timedelta
from typing import Optional

from envchain.chain import get_chain, add_chain, get_chain_names


class RetentionError(Exception):
    pass


def _parse_days(days: int) -> int:
    if not isinstance(days, int) or days <= 0:
        raise RetentionError(f"Retention days must be a positive integer, got: {days!r}")
    return days


def set_retention(chain_name: str, days: int, password: str) -> None:
    """Set a retention policy (in days) on a chain."""
    _parse_days(days)
    chain = get_chain(chain_name, password)
    meta = chain.get("__meta__", {})
    meta["retention_days"] = days
    meta["retention_set_at"] = datetime.utcnow().isoformat()
    chain["__meta__"] = meta
    add_chain(chain_name, chain, password, overwrite=True)


def get_retention(chain_name: str, password: str) -> Optional[int]:
    """Return the retention period in days, or None if not set."""
    chain = get_chain(chain_name, password)
    meta = chain.get("__meta__", {})
    return meta.get("retention_days")


def clear_retention(chain_name: str, password: str) -> None:
    """Remove the retention policy from a chain."""
    chain = get_chain(chain_name, password)
    meta = chain.get("__meta__", {})
    meta.pop("retention_days", None)
    meta.pop("retention_set_at", None)
    chain["__meta__"] = meta
    add_chain(chain_name, chain, password, overwrite=True)


def is_retention_expired(chain_name: str, password: str) -> bool:
    """Return True if the chain has exceeded its retention period."""
    chain = get_chain(chain_name, password)
    meta = chain.get("__meta__", {})
    days = meta.get("retention_days")
    set_at = meta.get("retention_set_at")
    if days is None or set_at is None:
        return False
    created = datetime.fromisoformat(set_at)
    return datetime.utcnow() >= created + timedelta(days=days)


def list_expired_retention(password: str) -> list:
    """Return names of chains whose retention period has expired."""
    expired = []
    for name in get_chain_names(password):
        try:
            if is_retention_expired(name, password):
                expired.append(name)
        except Exception:
            continue
    return expired
