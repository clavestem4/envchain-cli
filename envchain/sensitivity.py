"""Sensitivity classification for envchain chains.

Allows marking chains with a sensitivity level (e.g., public, internal,
confidential, secret) to help users understand the risk level of stored
variables and enforce handling policies.
"""

from __future__ import annotations

from typing import Callable

VALID_LEVELS = ("public", "internal", "confidential", "secret")

_META_KEY = "__sensitivity__"


class SensitivityError(Exception):
    """Raised when a sensitivity operation fails."""


def set_sensitivity(
    chain_name: str,
    level: str,
    password: str,
    *,
    get_chain: Callable,
    add_chain: Callable,
) -> None:
    """Set the sensitivity level for a chain.

    Args:
        chain_name: Name of the chain to update.
        level: Sensitivity level; must be one of VALID_LEVELS.
        password: Encryption password.
        get_chain: Callable to retrieve a chain by name and password.
        add_chain: Callable to persist the updated chain.

    Raises:
        SensitivityError: If the chain does not exist or the level is invalid.
    """
    if level not in VALID_LEVELS:
        raise SensitivityError(
            f"Invalid sensitivity level '{level}'. "
            f"Choose from: {', '.join(VALID_LEVELS)}"
        )

    try:
        data = get_chain(chain_name, password)
    except Exception as exc:
        raise SensitivityError(f"Chain '{chain_name}' not found.") from exc

    data[_META_KEY] = level
    add_chain(chain_name, password, data, overwrite=True)


def get_sensitivity(
    chain_name: str,
    password: str,
    *,
    get_chain: Callable,
) -> str | None:
    """Return the sensitivity level of a chain, or None if unset.

    Args:
        chain_name: Name of the chain.
        password: Encryption password.
        get_chain: Callable to retrieve a chain by name and password.

    Raises:
        SensitivityError: If the chain does not exist.
    """
    try:
        data = get_chain(chain_name, password)
    except Exception as exc:
        raise SensitivityError(f"Chain '{chain_name}' not found.") from exc

    return data.get(_META_KEY)


def clear_sensitivity(
    chain_name: str,
    password: str,
    *,
    get_chain: Callable,
    add_chain: Callable,
) -> None:
    """Remove the sensitivity classification from a chain.

    Args:
        chain_name: Name of the chain.
        password: Encryption password.
        get_chain: Callable to retrieve a chain by name and password.
        add_chain: Callable to persist the updated chain.

    Raises:
        SensitivityError: If the chain does not exist.
    """
    try:
        data = get_chain(chain_name, password)
    except Exception as exc:
        raise SensitivityError(f"Chain '{chain_name}' not found.") from exc

    data.pop(_META_KEY, None)
    add_chain(chain_name, password, data, overwrite=True)


def list_by_sensitivity(
    level: str,
    password: str,
    *,
    get_chain_names: Callable,
    get_chain: Callable,
) -> list[str]:
    """Return names of all chains whose sensitivity matches *level*.

    Args:
        level: The sensitivity level to filter by.
        password: Encryption password.
        get_chain_names: Callable returning all chain names.
        get_chain: Callable to retrieve a chain by name and password.

    Raises:
        SensitivityError: If the level is not valid.
    """
    if level not in VALID_LEVELS:
        raise SensitivityError(
            f"Invalid sensitivity level '{level}'. "
            f"Choose from: {', '.join(VALID_LEVELS)}"
        )

    results: list[str] = []
    for name in get_chain_names():
        try:
            data = get_chain(name, password)
        except Exception:
            continue
        if data.get(_META_KEY) == level:
            results.append(name)
    return results
