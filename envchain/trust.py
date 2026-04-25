"""Trust level management for envchain chains."""

from typing import Optional
from envchain.chain import get_chain, add_chain, get_chain_names

TRUST_LEVELS = ["untrusted", "low", "medium", "high", "verified"]
TRUST_KEY = "__trust__"


class TrustError(Exception):
    pass


def set_trust(chain_name: str, level: str, password: str) -> None:
    """Set the trust level for a chain."""
    if level not in TRUST_LEVELS:
        raise TrustError(
            f"Invalid trust level '{level}'. Must be one of: {', '.join(TRUST_LEVELS)}"
        )
    chain = get_chain(chain_name, password)
    chain[TRUST_KEY] = level
    add_chain(chain_name, chain, password)


def get_trust(chain_name: str, password: str) -> Optional[str]:
    """Get the trust level of a chain, or None if not set."""
    chain = get_chain(chain_name, password)
    return chain.get(TRUST_KEY)


def clear_trust(chain_name: str, password: str) -> None:
    """Remove the trust level from a chain."""
    chain = get_chain(chain_name, password)
    if TRUST_KEY in chain:
        del chain[TRUST_KEY]
        add_chain(chain_name, chain, password)


def list_by_trust(level: str, password: str) -> list:
    """Return all chain names with a given trust level."""
    if level not in TRUST_LEVELS:
        raise TrustError(
            f"Invalid trust level '{level}'. Must be one of: {', '.join(TRUST_LEVELS)}"
        )
    results = []
    for name in get_chain_names(password):
        chain = get_chain(name, password)
        if chain.get(TRUST_KEY) == level:
            results.append(name)
    return results
