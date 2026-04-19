"""Group multiple chains under a named group for batch operations."""

from envchain.chain import get_chain, add_chain, get_chain_names


class GroupError(Exception):
    pass


def _get_groups(meta_chain: dict) -> dict:
    return meta_chain.get("__groups__", {})


def create_group(group_name: str, chain_names: list, get_chain_fn=get_chain, add_chain_fn=add_chain):
    """Create a named group containing references to existing chains."""
    meta = {}
    try:
        meta = get_chain_fn("__meta__")
    except Exception:
        pass

    all_chains = get_chain_names()
    missing = [c for c in chain_names if c not in all_chains]
    if missing:
        raise GroupError(f"Chains not found: {', '.join(missing)}")

    groups = _get_groups(meta)
    groups[group_name] = list(chain_names)
    meta["__groups__"] = groups
    add_chain_fn("__meta__", meta)


def get_group(group_name: str, get_chain_fn=get_chain) -> list:
    """Return list of chain names in a group."""
    meta = {}
    try:
        meta = get_chain_fn("__meta__")
    except Exception:
        pass
    groups = _get_groups(meta)
    if group_name not in groups:
        raise GroupError(f"Group '{group_name}' not found")
    return groups[group_name]


def delete_group(group_name: str, get_chain_fn=get_chain, add_chain_fn=add_chain):
    """Remove a group definition."""
    meta = {}
    try:
        meta = get_chain_fn("__meta__")
    except Exception:
        pass
    groups = _get_groups(meta)
    if group_name not in groups:
        raise GroupError(f"Group '{group_name}' not found")
    del groups[group_name]
    meta["__groups__"] = groups
    add_chain_fn("__meta__", meta)


def list_groups(get_chain_fn=get_chain) -> dict:
    """Return all group definitions."""
    meta = {}
    try:
        meta = get_chain_fn("__meta__")
    except Exception:
        pass
    return _get_groups(meta)
