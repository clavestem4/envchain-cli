"""Higher-level helpers that combine lineage with chain data."""

from envchain.lineage import get_parent, get_children, get_ancestors, LineageError
from envchain.chain import get_chain


def inherited_vars(chain_name: str, password: str) -> dict:
    """Return merged env vars from all ancestors (nearest ancestor wins).

    Variables defined closer to the chain take precedence over those
    from more distant ancestors.
    """
    ancestors = get_ancestors(chain_name, password)
    merged: dict = {}
    # Apply from most-distant to nearest so closer ancestors override
    for anc in reversed(ancestors):
        try:
            data = get_chain(anc, password)
            for k, v in data.items():
                if not k.startswith("__"):
                    merged[k] = v
        except Exception:
            pass
    return merged


def effective_vars(chain_name: str, password: str) -> dict:
    """Return the effective env vars for a chain, including inherited ones.

    Chain's own variables override inherited values.
    """
    base = inherited_vars(chain_name, password)
    own = get_chain(chain_name, password)
    for k, v in own.items():
        if not k.startswith("__"):
            base[k] = v
    return base


def lineage_tree(chain_name: str, password: str, _depth: int = 0) -> list[dict]:
    """Return a tree structure of *chain_name* and all its descendants.

    Each node is ``{"name": str, "depth": int, "children": list}``.
    """
    node: dict = {"name": chain_name, "depth": _depth, "children": []}
    try:
        children = get_children(chain_name, password)
    except Exception:
        children = []
    for child in children:
        node["children"].append(lineage_tree(child, password, _depth + 1))
    return node


def find_roots(password: str) -> list[str]:
    """Return all chains that have no parent (root chains)."""
    from envchain.chain import get_chain_names
    roots = []
    for name in get_chain_names(password):
        try:
            parent = get_parent(name, password)
            if parent is None:
                roots.append(name)
        except Exception:
            roots.append(name)
    return sorted(roots)
