"""Lifecycle state management for chains (draft, active, deprecated, archived)."""

from envchain.chain import get_chain, add_chain, get_chain_names

VALID_STATES = {"draft", "active", "deprecated", "archived"}
_META_KEY = "__lifecycle__"


class LifecycleError(Exception):
    pass


def set_lifecycle(chain_name: str, state: str, password: str) -> None:
    """Set the lifecycle state of a chain."""
    if state not in VALID_STATES:
        raise LifecycleError(
            f"Invalid state '{state}'. Must be one of: {', '.join(sorted(VALID_STATES))}"
        )
    chain = get_chain(chain_name, password)
    if chain is None:
        raise LifecycleError(f"Chain '{chain_name}' not found.")
    chain[_META_KEY] = state
    add_chain(chain_name, chain, password, overwrite=True)


def get_lifecycle(chain_name: str, password: str) -> str | None:
    """Get the lifecycle state of a chain, or None if unset."""
    chain = get_chain(chain_name, password)
    if chain is None:
        raise LifecycleError(f"Chain '{chain_name}' not found.")
    return chain.get(_META_KEY)


def clear_lifecycle(chain_name: str, password: str) -> None:
    """Remove the lifecycle state from a chain."""
    chain = get_chain(chain_name, password)
    if chain is None:
        raise LifecycleError(f"Chain '{chain_name}' not found.")
    chain.pop(_META_KEY, None)
    add_chain(chain_name, chain, password, overwrite=True)


def list_by_lifecycle(state: str, password: str) -> list[str]:
    """Return all chain names that have the given lifecycle state."""
    if state not in VALID_STATES:
        raise LifecycleError(
            f"Invalid state '{state}'. Must be one of: {', '.join(sorted(VALID_STATES))}"
        )
    result = []
    for name in get_chain_names(password):
        chain = get_chain(name, password)
        if chain and chain.get(_META_KEY) == state:
            result.append(name)
    return result
