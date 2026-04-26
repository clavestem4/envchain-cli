"""Integration helpers for sensitivity-aware chain operations."""
from __future__ import annotations

from envchain.sensitivity import get_sensitivity, list_by_sensitivity, VALID_LEVELS


def sensitivity_summary(
    password: str,
    get_chain_names_fn,
    get_chain_fn,
) -> dict[str, str | None]:
    """Return a mapping of chain_name -> sensitivity level for all chains."""
    summary: dict[str, str | None] = {}
    for name in get_chain_names_fn():
        try:
            level = get_sensitivity(name, password, get_chain_fn)
        except Exception:
            level = None
        summary[name] = level
    return summary


def chains_above_level(
    threshold: str,
    password: str,
    get_chain_names_fn,
    get_chain_fn,
) -> list[str]:
    """Return chains whose sensitivity is at or above the given threshold."""
    levels = list(VALID_LEVELS)
    ordered = ["public", "internal", "confidential", "secret", "top-secret"]
    if threshold not in ordered:
        raise ValueError(f"Unknown sensitivity level: {threshold}")
    threshold_idx = ordered.index(threshold)
    result = []
    for name in get_chain_names_fn():
        try:
            level = get_sensitivity(name, password, get_chain_fn)
        except Exception:
            continue
        if level and ordered.index(level) >= threshold_idx:
            result.append(name)
    return result


def filter_public_chains(
    password: str,
    get_chain_names_fn,
    get_chain_fn,
) -> list[str]:
    """Return only chains explicitly marked as public."""
    return list_by_sensitivity("public", password, get_chain_names_fn, get_chain_fn)
