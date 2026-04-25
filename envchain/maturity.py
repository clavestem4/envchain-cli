"""Maturity level tracking for chains."""

from envchain.chain import get_chain, add_chain, get_chain_names

MATURITY_LEVELS = ["experimental", "developing", "stable", "deprecated", "archived"]
METAKEY = "__maturity__"


class MaturityError(Exception):
    pass


def set_maturity(chain_name: str, level: str, password: str) -> None:
    """Set the maturity level for a chain."""
    if level not in MATURITY_LEVELS:
        raise MaturityError(
            f"Invalid maturity level '{level}'. Must be one of: {', '.join(MATURITY_LEVELS)}"
        )
    chain = get_chain(chain_name, password)
    chain[METAKEY] = level
    add_chain(chain_name, chain, password, overwrite=True)


def get_maturity(chain_name: str, password: str) -> str | None:
    """Get the maturity level of a chain, or None if not set."""
    chain = get_chain(chain_name, password)
    return chain.get(METAKEY)


def clear_maturity(chain_name: str, password: str) -> None:
    """Remove the maturity level from a chain."""
    chain = get_chain(chain_name, password)
    if METAKEY in chain:
        del chain[METAKEY]
        add_chain(chain_name, chain, password, overwrite=True)


def list_by_maturity(level: str, password: str) -> list[str]:
    """Return all chain names that have the given maturity level."""
    if level not in MATURITY_LEVELS:
        raise MaturityError(
            f"Invalid maturity level '{level}'. Must be one of: {', '.join(MATURITY_LEVELS)}"
        )
    results = []
    for name in get_chain_names(password):
        chain = get_chain(name, password)
        if chain.get(METAKEY) == level:
            results.append(name)
    return results
