"""Archetype module: assign and query predefined chain archetypes (e.g. 'database', 'api', 'service')."""

from typing import Optional
from envchain.chain import get_chain, add_chain, get_chain_names

VALID_ARCHETYPES = {
    "database",
    "api",
    "service",
    "storage",
    "messaging",
    "auth",
    "cache",
    "generic",
}

ARCHETYPE_KEY = "__archetype__"


class ArchetypeError(Exception):
    pass


def set_archetype(chain_name: str, archetype: str, password: str) -> None:
    """Assign an archetype to a chain."""
    if archetype not in VALID_ARCHETYPES:
        raise ArchetypeError(
            f"Invalid archetype '{archetype}'. Valid options: {sorted(VALID_ARCHETYPES)}"
        )
    chain = get_chain(chain_name, password)
    chain[ARCHETYPE_KEY] = archetype
    add_chain(chain_name, chain, password, overwrite=True)


def get_archetype(chain_name: str, password: str) -> Optional[str]:
    """Return the archetype of a chain, or None if not set."""
    chain = get_chain(chain_name, password)
    return chain.get(ARCHETYPE_KEY)


def clear_archetype(chain_name: str, password: str) -> None:
    """Remove the archetype from a chain."""
    chain = get_chain(chain_name, password)
    if ARCHETYPE_KEY in chain:
        del chain[ARCHETYPE_KEY]
        add_chain(chain_name, chain, password, overwrite=True)


def list_by_archetype(archetype: str, password: str) -> list:
    """Return all chain names that have the given archetype."""
    if archetype not in VALID_ARCHETYPES:
        raise ArchetypeError(
            f"Invalid archetype '{archetype}'. Valid options: {sorted(VALID_ARCHETYPES)}"
        )
    results = []
    for name in get_chain_names(password):
        chain = get_chain(name, password)
        if chain.get(ARCHETYPE_KEY) == archetype:
            results.append(name)
    return results
