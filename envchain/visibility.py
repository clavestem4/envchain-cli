"""Visibility control for chains (public/private/shared)."""

from envchain.chain import get_chain, add_chain, get_chain_names

VALID_LEVELS = ("public", "private", "shared")
_KEY = "__visibility__"


class VisibilityError(Exception):
    pass


def set_visibility(chain_name: str, level: str, password: str) -> None:
    if level not in VALID_LEVELS:
        raise VisibilityError(f"Invalid visibility level '{level}'. Choose from: {', '.join(VALID_LEVELS)}")
    chain = get_chain(chain_name, password)
    chain[_KEY] = level
    add_chain(chain_name, chain, password, overwrite=True)


def get_visibility(chain_name: str, password: str) -> str:
    chain = get_chain(chain_name, password)
    return chain.get(_KEY, "private")


def clear_visibility(chain_name: str, password: str) -> None:
    chain = get_chain(chain_name, password)
    chain.pop(_KEY, None)
    add_chain(chain_name, chain, password, overwrite=True)


def list_by_visibility(level: str, password: str) -> list:
    if level not in VALID_LEVELS:
        raise VisibilityError(f"Invalid visibility level '{level}'.")
    results = []
    for name in get_chain_names(password):
        try:
            chain = get_chain(name, password)
            if chain.get(_KEY, "private") == level:
                results.append(name)
        except Exception:
            continue
    return results
