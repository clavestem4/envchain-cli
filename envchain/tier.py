"""Tier management for envchain chains.

Allows assigning a tier level (e.g. free, pro, enterprise) to a chain,
useful for organizing chains by service tier or access level.
"""

from envchain.chain import get_chain, add_chain, get_chain_names

VALID_TIERS = {"free", "pro", "enterprise", "internal", "legacy"}
_TIER_KEY = "__tier__"


class TierError(Exception):
    pass


def set_tier(chain_name: str, tier: str, password: str) -> None:
    """Set the tier for a chain."""
    if tier not in VALID_TIERS:
        raise TierError(
            f"Invalid tier '{tier}'. Valid tiers: {sorted(VALID_TIERS)}"
        )
    try:
        data = get_chain(chain_name, password)
    except KeyError:
        raise TierError(f"Chain '{chain_name}' not found.")
    data[_TIER_KEY] = tier
    add_chain(chain_name, data, password, overwrite=True)


def get_tier(chain_name: str, password: str) -> str | None:
    """Get the tier for a chain, or None if not set."""
    try:
        data = get_chain(chain_name, password)
    except KeyError:
        raise TierError(f"Chain '{chain_name}' not found.")
    return data.get(_TIER_KEY)


def clear_tier(chain_name: str, password: str) -> None:
    """Remove the tier assignment from a chain."""
    try:
        data = get_chain(chain_name, password)
    except KeyError:
        raise TierError(f"Chain '{chain_name}' not found.")
    data.pop(_TIER_KEY, None)
    add_chain(chain_name, data, password, overwrite=True)


def list_by_tier(tier: str, password: str) -> list[str]:
    """Return all chain names assigned to the given tier."""
    if tier not in VALID_TIERS:
        raise TierError(
            f"Invalid tier '{tier}'. Valid tiers: {sorted(VALID_TIERS)}"
        )
    results = []
    for name in get_chain_names(password):
        try:
            data = get_chain(name, password)
            if data.get(_TIER_KEY) == tier:
                results.append(name)
        except Exception:
            continue
    return results
