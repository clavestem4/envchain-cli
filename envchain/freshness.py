from datetime import datetime, timezone, timedelta
from typing import Optional

META_KEY = "__freshness__"
VALID_UNITS = {"minutes", "hours", "days", "weeks"}


class FreshnessError(Exception):
    pass


def _parse_max_age(value: str) -> timedelta:
    """Parse a string like '30 minutes' or '7 days' into a timedelta."""
    parts = value.strip().split()
    if len(parts) != 2:
        raise FreshnessError(f"Invalid max_age format: '{value}'. Expected '<number> <unit>'")
    try:
        amount = int(parts[0])
    except ValueError:
        raise FreshnessError(f"Invalid amount in max_age: '{parts[0]}'")
    unit = parts[1].lower().rstrip("s") + "s"
    if unit not in VALID_UNITS:
        raise FreshnessError(f"Invalid unit '{parts[1]}'. Must be one of: {', '.join(sorted(VALID_UNITS))}")
    return timedelta(**{unit: amount})


def set_freshness(chain_name: str, max_age: str, get_chain, add_chain) -> None:
    """Set the freshness policy (max_age) for a chain."""
    _parse_max_age(max_age)  # validate early
    data = get_chain(chain_name)
    if data is None:
        raise FreshnessError(f"Chain '{chain_name}' not found")
    meta = data.get(META_KEY, {})
    meta["max_age"] = max_age
    meta["updated_at"] = datetime.now(timezone.utc).isoformat()
    data[META_KEY] = meta
    add_chain(chain_name, data, overwrite=True)


def get_freshness(chain_name: str, get_chain) -> Optional[dict]:
    """Return the freshness metadata for a chain, or None if not set."""
    data = get_chain(chain_name)
    if data is None:
        raise FreshnessError(f"Chain '{chain_name}' not found")
    return data.get(META_KEY)


def clear_freshness(chain_name: str, get_chain, add_chain) -> None:
    """Remove freshness policy from a chain."""
    data = get_chain(chain_name)
    if data is None:
        raise FreshnessError(f"Chain '{chain_name}' not found")
    data.pop(META_KEY, None)
    add_chain(chain_name, data, overwrite=True)


def is_stale(chain_name: str, get_chain) -> bool:
    """Return True if the chain's freshness policy has been exceeded."""
    data = get_chain(chain_name)
    if data is None:
        raise FreshnessError(f"Chain '{chain_name}' not found")
    meta = data.get(META_KEY)
    if not meta or "max_age" not in meta or "updated_at" not in meta:
        return False
    max_age = _parse_max_age(meta["max_age"])
    updated_at = datetime.fromisoformat(meta["updated_at"])
    return datetime.now(timezone.utc) - updated_at > max_age


def list_stale(get_chain_names, get_chain) -> list:
    """Return list of chain names whose freshness has expired."""
    return [name for name in get_chain_names() if is_stale(name, get_chain)]
