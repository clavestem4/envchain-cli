"""Permission module: assign read/write/exec permissions to chains."""

from envchain.chain import get_chain, add_chain, get_chain_names

VALID_PERMISSIONS = {"read", "write", "exec"}
_PERM_KEY = "__permissions__"


class PermissionError(Exception):
    pass


def _get_perms(chain_name: str) -> dict:
    chain = get_chain(chain_name)
    return chain.get(_PERM_KEY, {})


def set_permission(chain_name: str, user: str, permissions: list[str]) -> None:
    """Set permissions for a user on a chain."""
    invalid = set(permissions) - VALID_PERMISSIONS
    if invalid:
        raise PermissionError(f"Invalid permissions: {', '.join(sorted(invalid))}")
    chain = get_chain(chain_name)
    perms = chain.get(_PERM_KEY, {})
    perms[user] = sorted(set(permissions))
    chain[_PERM_KEY] = perms
    add_chain(chain_name, chain, overwrite=True)


def get_permission(chain_name: str, user: str) -> list[str]:
    """Return the list of permissions for a user on a chain."""
    perms = _get_perms(chain_name)
    return perms.get(user, [])


def revoke_permission(chain_name: str, user: str) -> None:
    """Remove all permissions for a user on a chain."""
    chain = get_chain(chain_name)
    perms = chain.get(_PERM_KEY, {})
    if user not in perms:
        raise PermissionError(f"User '{user}' has no permissions on '{chain_name}'")
    del perms[user]
    chain[_PERM_KEY] = perms
    add_chain(chain_name, chain, overwrite=True)


def has_permission(chain_name: str, user: str, permission: str) -> bool:
    """Check if a user has a specific permission on a chain."""
    return permission in get_permission(chain_name, user)


def list_permissions(chain_name: str) -> dict[str, list[str]]:
    """Return all user permissions for a chain."""
    return dict(_get_perms(chain_name))


def find_chains_for_user(user: str, permission: str | None = None) -> list[str]:
    """Return all chain names where the user has any (or specific) permission."""
    results = []
    for name in get_chain_names():
        try:
            perms = get_permission(name, user)
            if perms and (permission is None or permission in perms):
                results.append(name)
        except Exception:
            continue
    return results
