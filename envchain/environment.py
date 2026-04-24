"""Environment profile management for envchain.

Allows chains to be associated with named environment profiles
(e.g. 'production', 'staging', 'development') for easier filtering.
"""

from typing import Optional
from envchain.chain import get_chain, add_chain, get_chain_names

ENV_PROFILE_KEY = "__env_profile__"


class EnvironmentError(Exception):
    pass


VALID_PROFILES = {"development", "staging", "production", "testing", "local"}


def set_environment(chain_name: str, profile: str, password: str) -> None:
    """Assign an environment profile to a chain."""
    if profile not in VALID_PROFILES:
        raise EnvironmentError(
            f"Invalid profile '{profile}'. Must be one of: {', '.join(sorted(VALID_PROFILES))}"
        )
    try:
        data = get_chain(chain_name, password)
    except KeyError:
        raise EnvironmentError(f"Chain '{chain_name}' not found.")
    data[ENV_PROFILE_KEY] = profile
    add_chain(chain_name, data, password, overwrite=True)


def get_environment(chain_name: str, password: str) -> Optional[str]:
    """Return the environment profile for a chain, or None if unset."""
    try:
        data = get_chain(chain_name, password)
    except KeyError:
        raise EnvironmentError(f"Chain '{chain_name}' not found.")
    return data.get(ENV_PROFILE_KEY)


def clear_environment(chain_name: str, password: str) -> None:
    """Remove the environment profile from a chain."""
    try:
        data = get_chain(chain_name, password)
    except KeyError:
        raise EnvironmentError(f"Chain '{chain_name}' not found.")
    data.pop(ENV_PROFILE_KEY, None)
    add_chain(chain_name, data, password, overwrite=True)


def list_by_environment(profile: str, password: str) -> list[str]:
    """Return all chain names assigned to the given environment profile."""
    if profile not in VALID_PROFILES:
        raise EnvironmentError(
            f"Invalid profile '{profile}'. Must be one of: {', '.join(sorted(VALID_PROFILES))}"
        )
    results = []
    for name in get_chain_names(password):
        try:
            data = get_chain(name, password)
            if data.get(ENV_PROFILE_KEY) == profile:
                results.append(name)
        except Exception:
            continue
    return results
