"""Integration helpers: apply chain priority ordering to multi-chain operations."""

from envchain.priority import list_by_priority
from envchain.chain import get_chain


def get_chains_by_priority(password: str, exclude_meta: bool = True) -> list[tuple[str, dict]]:
    """Return (name, vars) tuples for all chains ordered by priority.

    Args:
        password: Master password.
        exclude_meta: If True, strip internal __ keys from returned vars.

    Returns:
        List of (chain_name, variables) sorted by priority ascending.
    """
    ordered = list_by_priority(password)
    result = []
    for name, _priority in ordered:
        try:
            chain = get_chain(name, password)
        except Exception:
            continue
        if exclude_meta:
            chain = {k: v for k, v in chain.items() if not (k.startswith("__") and k.endswith("__"))}
        result.append((name, chain))
    return result


def merge_by_priority(password: str) -> dict:
    """Merge all chains into a single env dict, higher priority (lower number) wins.

    Chains with lower priority numbers override those with higher numbers.
    Chains with no priority are applied last (lowest precedence).

    Returns:
        Merged dict of environment variables.
    """
    chains = get_chains_by_priority(password, exclude_meta=True)
    # Reverse so highest priority (lowest number) applied last and wins
    merged: dict = {}
    for _name, variables in reversed(chains):
        merged.update(variables)
    return merged


def find_chain_for_key(key: str, password: str) -> str | None:
    """Find the highest-priority chain that defines a given key.

    Args:
        key: The environment variable name to search for.
        password: Master password.

    Returns:
        The name of the highest-priority chain containing the key,
        or None if no chain defines it.
    """
    for name, variables in get_chains_by_priority(password, exclude_meta=True):
        if key in variables:
            return name
    return None
