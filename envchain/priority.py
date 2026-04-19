"""Priority ranking for chains."""

from envchain.chain import get_chain, add_chain, get_chain_names

PRIORITY_KEY = "__priority__"


class PriorityError(Exception):
    pass


def set_priority(chain_name: str, priority: int, password: str) -> None:
    """Set numeric priority for a chain (lower = higher priority)."""
    chain = get_chain(chain_name, password)
    chain[PRIORITY_KEY] = str(priority)
    add_chain(chain_name, chain, password, overwrite=True)


def get_priority(chain_name: str, password: str) -> int | None:
    """Return priority of a chain, or None if not set."""
    chain = get_chain(chain_name, password)
    val = chain.get(PRIORITY_KEY)
    return int(val) if val is not None else None


def clear_priority(chain_name: str, password: str) -> None:
    """Remove priority from a chain."""
    chain = get_chain(chain_name, password)
    if PRIORITY_KEY not in chain:
        raise PriorityError(f"Chain '{chain_name}' has no priority set.")
    del chain[PRIORITY_KEY]
    add_chain(chain_name, chain, password, overwrite=True)


def list_by_priority(password: str) -> list[tuple[str, int | None]]:
    """Return all chains sorted by priority (unset last)."""
    names = get_chain_names(password)
    results = []
    for name in names:
        try:
            p = get_priority(name, password)
        except Exception:
            p = None
        results.append((name, p))
    results.sort(key=lambda x: (x[1] is None, x[1]))
    return results
