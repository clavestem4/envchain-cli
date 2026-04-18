"""TTL (time-to-live) support for chains — auto-expire after a duration."""

from datetime import datetime, timedelta, timezone
from typing import Optional
from envchain.chain import get_chain, add_chain, get_chain_names

_TTL_KEY = "__ttl_seconds__"
_TTL_SET_AT_KEY = "__ttl_set_at__"


def set_ttl(chain_name: str, password: str, seconds: int) -> None:
    """Set a TTL (in seconds) on a chain."""
    if seconds <= 0:
        raise ValueError("TTL must be a positive integer number of seconds.")
    data = get_chain(chain_name, password)
    data[_TTL_KEY] = str(seconds)
    data[_TTL_SET_AT_KEY] = datetime.now(timezone.utc).isoformat()
    add_chain(chain_name, password, data, overwrite=True)


def get_ttl(chain_name: str, password: str) -> Optional[dict]:
    """Return TTL info dict with 'seconds', 'set_at', 'expires_at', 'expired'."""
    data = get_chain(chain_name, password)
    if _TTL_KEY not in data or _TTL_SET_AT_KEY not in data:
        return None
    seconds = int(data[_TTL_KEY])
    set_at = datetime.fromisoformat(data[_TTL_SET_AT_KEY])
    expires_at = set_at + timedelta(seconds=seconds)
    now = datetime.now(timezone.utc)
    return {
        "seconds": seconds,
        "set_at": set_at,
        "expires_at": expires_at,
        "expired": now >= expires_at,
    }


def clear_ttl(chain_name: str, password: str) -> None:
    """Remove TTL metadata from a chain."""
    data = get_chain(chain_name, password)
    data.pop(_TTL_KEY, None)
    data.pop(_TTL_SET_AT_KEY, None)
    add_chain(chain_name, password, data, overwrite=True)


def is_ttl_expired(chain_name: str, password: str) -> bool:
    """Return True if the chain has an expired TTL."""
    info = get_ttl(chain_name, password)
    return info is not None and info["expired"]


def list_expired_ttl(password: str) -> list:
    """Return list of chain names whose TTL has expired."""
    expired = []
    for name in get_chain_names(password):
        try:
            if is_ttl_expired(name, password):
                expired.append(name)
        except Exception:
            continue
    return expired
