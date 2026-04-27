"""Impact level management for chains."""

from envchain.chain import get_chain, update_chain, get_chain_names

VALID_LEVELS = ("none", "low", "medium", "high", "critical")


class ImpactError(Exception):
    pass


def set_impact(chain_name: str, level: str, password: str) -> None:
    """Set the impact level for a chain."""
    level = level.lower()
    if level not in VALID_LEVELS:
        raise ImpactError(
            f"Invalid impact level '{level}'. Must be one of: {', '.join(VALID_LEVELS)}"
        )
    chain = get_chain(chain_name, password)
    chain["__impact__"] = level
    update_chain(chain_name, chain, password)


def get_impact(chain_name: str, password: str) -> str | None:
    """Get the impact level for a chain, or None if not set."""
    chain = get_chain(chain_name, password)
    return chain.get("__impact__")


def clear_impact(chain_name: str, password: str) -> None:
    """Remove the impact level from a chain."""
    chain = get_chain(chain_name, password)
    chain.pop("__impact__", None)
    update_chain(chain_name, chain, password)


def list_by_impact(level: str, password: str) -> list[str]:
    """Return all chain names that have the given impact level."""
    level = level.lower()
    if level not in VALID_LEVELS:
        raise ImpactError(
            f"Invalid impact level '{level}'. Must be one of: {', '.join(VALID_LEVELS)}"
        )
    results = []
    for name in get_chain_names(password):
        chain = get_chain(name, password)
        if chain.get("__impact__") == level:
            results.append(name)
    return results
