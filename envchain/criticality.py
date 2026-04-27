"""Criticality level management for chains."""

from typing import Optional
from envchain.chain import get_chain, update_chain, get_chain_names

VALID_LEVELS = ("low", "medium", "high", "critical")
META_KEY = "__criticality__"


class CriticalityError(Exception):
    pass


def set_criticality(chain_name: str, level: str, password: str) -> None:
    """Set the criticality level for a chain."""
    level = level.lower()
    if level not in VALID_LEVELS:
        raise CriticalityError(
            f"Invalid criticality level '{level}'. Must be one of: {', '.join(VALID_LEVELS)}"
        )
    chain = get_chain(chain_name, password)
    chain[META_KEY] = level
    update_chain(chain_name, chain, password)


def get_criticality(chain_name: str, password: str) -> Optional[str]:
    """Get the criticality level for a chain, or None if unset."""
    chain = get_chain(chain_name, password)
    return chain.get(META_KEY)


def clear_criticality(chain_name: str, password: str) -> None:
    """Remove the criticality level from a chain."""
    chain = get_chain(chain_name, password)
    if META_KEY in chain:
        del chain[META_KEY]
        update_chain(chain_name, chain, password)


def list_by_criticality(level: str, password: str) -> list:
    """Return all chain names that have the given criticality level."""
    level = level.lower()
    if level not in VALID_LEVELS:
        raise CriticalityError(
            f"Invalid criticality level '{level}'. Must be one of: {', '.join(VALID_LEVELS)}"
        )
    results = []
    for name in get_chain_names(password):
        chain = get_chain(name, password)
        if chain.get(META_KEY) == level:
            results.append(name)
    return results
