"""Track chain lineage — parent/child relationships between chains."""

from envchain.chain import get_chain, add_chain, get_chain_names


class LineageError(Exception):
    pass


META_KEY = "__lineage__"


def _get_lineage(chain: dict) -> dict:
    raw = chain.get(META_KEY)
    if isinstance(raw, dict):
        return raw
    return {}


def set_parent(chain_name: str, parent_name: str, password: str) -> None:
    """Declare *parent_name* as the parent of *chain_name*."""
    all_names = get_chain_names(password)
    if chain_name not in all_names:
        raise LineageError(f"Chain '{chain_name}' not found.")
    if parent_name not in all_names:
        raise LineageError(f"Parent chain '{parent_name}' not found.")
    if parent_name == chain_name:
        raise LineageError("A chain cannot be its own parent.")

    chain = get_chain(chain_name, password)
    lineage = _get_lineage(chain)
    lineage["parent"] = parent_name
    chain[META_KEY] = lineage
    add_chain(chain_name, chain, password, overwrite=True)


def get_parent(chain_name: str, password: str) -> str | None:
    """Return the parent chain name, or None if unset."""
    chain = get_chain(chain_name, password)
    return _get_lineage(chain).get("parent")


def clear_parent(chain_name: str, password: str) -> None:
    """Remove parent declaration from *chain_name*."""
    chain = get_chain(chain_name, password)
    lineage = _get_lineage(chain)
    lineage.pop("parent", None)
    if lineage:
        chain[META_KEY] = lineage
    else:
        chain.pop(META_KEY, None)
    add_chain(chain_name, chain, password, overwrite=True)


def get_children(chain_name: str, password: str) -> list[str]:
    """Return all chains that declare *chain_name* as their parent."""
    children = []
    for name in get_chain_names(password):
        if name == chain_name:
            continue
        try:
            parent = get_parent(name, password)
            if parent == chain_name:
                children.append(name)
        except Exception:
            pass
    return sorted(children)


def get_ancestors(chain_name: str, password: str) -> list[str]:
    """Return the ordered list of ancestors (nearest first)."""
    ancestors: list[str] = []
    visited: set[str] = set()
    current = chain_name
    while True:
        parent = get_parent(current, password)
        if parent is None or parent in visited:
            break
        ancestors.append(parent)
        visited.add(parent)
        current = parent
    return ancestors
