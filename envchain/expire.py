"""Expiry support for chains — store and check TTL metadata."""

from datetime import datetime, timezone
from envchain.chain import get_chain, add_chain, get_chain_names

EXPIRY_KEY = "__expires_at__"


def set_expiry(chain_name: str, password: str, expires_at: datetime) -> None:
    """Set an expiry timestamp on a chain."""
    chain = get_chain(chain_name, password)
    chain[EXPIRY_KEY] = expires_at.astimezone(timezone.utc).isoformat()
    add_chain(chain_name, password, chain, overwrite=True)


def get_expiry(chain_name: str, password: str) -> datetime | None:
    """Return the expiry datetime for a chain, or None if not set."""
    chain = get_chain(chain_name, password)
    raw = chain.get(EXPIRY_KEY)
    if raw is None:
        return None
    return datetime.fromisoformat(raw)


def clear_expiry(chain_name: str, password: str) -> None:
    """Remove expiry metadata from a chain."""
    chain = get_chain(chain_name, password)
    if EXPIRY_KEY in chain:
        del chain[EXPIRY_KEY]
        add_chain(chain_name, password, chain, overwrite=True)


def is_expired(chain_name: str, password: str) -> bool:
    """Return True if the chain has passed its expiry time."""
    expiry = get_expiry(chain_name, password)
    if expiry is None:
        return False
    return datetime.now(timezone.utc) >= expiry


def list_expired(password: str) -> list[str]:
    """Return names of all chains that are currently expired."""
    expired = []
    for name in get_chain_names():
        try:
            if is_expired(name, password):
                expired.append(name)
        except Exception:
            continue
    return expired
