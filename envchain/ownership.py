"""Ownership tracking for chains — assign an owner (user/team) to a chain."""

from envchain.chain import get_chain, add_chain, get_chain_names

OWNERSHIP_KEY = "__ownership__"


class OwnershipError(Exception):
    pass


def set_owner(chain_name: str, owner: str, password: str) -> None:
    """Set the owner of a chain."""
    if not owner or not owner.strip():
        raise OwnershipError("Owner must not be empty.")
    try:
        data = get_chain(chain_name, password)
    except KeyError:
        raise OwnershipError(f"Chain '{chain_name}' does not exist.")
    data[OWNERSHIP_KEY] = owner.strip()
    add_chain(chain_name, data, password, overwrite=True)


def get_owner(chain_name: str, password: str) -> str | None:
    """Return the owner of a chain, or None if unset."""
    try:
        data = get_chain(chain_name, password)
    except KeyError:
        raise OwnershipError(f"Chain '{chain_name}' does not exist.")
    return data.get(OWNERSHIP_KEY)


def clear_owner(chain_name: str, password: str) -> None:
    """Remove ownership metadata from a chain."""
    try:
        data = get_chain(chain_name, password)
    except KeyError:
        raise OwnershipError(f"Chain '{chain_name}' does not exist.")
    data.pop(OWNERSHIP_KEY, None)
    add_chain(chain_name, data, password, overwrite=True)


def list_by_owner(owner: str, password: str) -> list[str]:
    """Return all chain names owned by the given owner."""
    results = []
    for name in get_chain_names(password):
        try:
            data = get_chain(name, password)
            if data.get(OWNERSHIP_KEY) == owner:
                results.append(name)
        except Exception:
            continue
    return results
