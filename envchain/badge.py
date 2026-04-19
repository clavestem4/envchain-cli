"""Badge system for marking chains with status indicators."""

from typing import Optional
from envchain.chain import get_chain, add_chain

VALID_BADGES = {"stable", "experimental", "deprecated", "wip", "reviewed", "broken"}


class BadgeError(Exception):
    pass


def _get_badges(chain: dict) -> dict:
    meta = chain.get("__meta__", {})
    return meta.get("badges", {})


def set_badge(name: str, badge: str, password: str, note: str = "") -> None:
    if badge not in VALID_BADGES:
        raise BadgeError(f"Invalid badge '{badge}'. Choose from: {', '.join(sorted(VALID_BADGES))}")
    chain = get_chain(name, password)
    meta = chain.setdefault("__meta__", {})
    badges = meta.setdefault("badges", {})
    badges[badge] = note
    add_chain(name, chain, password, overwrite=True)


def remove_badge(name: str, badge: str, password: str) -> None:
    chain = get_chain(name, password)
    badges = chain.get("__meta__", {}).get("badges", {})
    if badge not in badges:
        raise BadgeError(f"Badge '{badge}' not set on chain '{name}'")
    del badges[badge]
    add_chain(name, chain, password, overwrite=True)


def get_badges(name: str, password: str) -> dict:
    chain = get_chain(name, password)
    return _get_badges(chain)


def find_by_badge(badge: str, password: str, get_chain_names_fn=None, get_chain_fn=None) -> list:
    from envchain.chain import get_chain_names
    names_fn = get_chain_names_fn or get_chain_names
    chain_fn = get_chain_fn or get_chain
    results = []
    for name in names_fn():
        try:
            chain = chain_fn(name, password)
            if badge in _get_badges(chain):
                results.append(name)
        except Exception:
            continue
    return results
