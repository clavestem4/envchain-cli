"""Scope management for envchain — assign a scope (e.g. 'dev', 'staging', 'prod') to a chain."""

from typing import Optional
from envchain.chain import get_chain, add_chain, get_chain_names

_SCOPE_KEY = "__scope__"

VALID_SCOPES = {"dev", "staging", "prod", "test", "local", "ci"}


class ScopeError(Exception):
    pass


def set_scope(chain_name: str, scope: str, password: str) -> None:
    """Assign a scope to the given chain."""
    if scope not in VALID_SCOPES:
        raise ScopeError(
            f"Invalid scope '{scope}'. Valid scopes: {', '.join(sorted(VALID_SCOPES))}"
        )
    try:
        data = get_chain(chain_name, password)
    except KeyError:
        raise ScopeError(f"Chain '{chain_name}' does not exist.")
    data[_SCOPE_KEY] = scope
    add_chain(chain_name, data, password, overwrite=True)


def get_scope(chain_name: str, password: str) -> Optional[str]:
    """Return the scope assigned to the given chain, or None if unset."""
    try:
        data = get_chain(chain_name, password)
    except KeyError:
        raise ScopeError(f"Chain '{chain_name}' does not exist.")
    return data.get(_SCOPE_KEY)


def clear_scope(chain_name: str, password: str) -> None:
    """Remove the scope from the given chain."""
    try:
        data = get_chain(chain_name, password)
    except KeyError:
        raise ScopeError(f"Chain '{chain_name}' does not exist.")
    data.pop(_SCOPE_KEY, None)
    add_chain(chain_name, data, password, overwrite=True)


def list_by_scope(scope: str, password: str) -> list:
    """Return all chain names that have the given scope."""
    if scope not in VALID_SCOPES:
        raise ScopeError(
            f"Invalid scope '{scope}'. Valid scopes: {', '.join(sorted(VALID_SCOPES))}"
        )
    results = []
    for name in get_chain_names(password):
        try:
            data = get_chain(name, password)
            if data.get(_SCOPE_KEY) == scope:
                results.append(name)
        except Exception:
            continue
    return results
