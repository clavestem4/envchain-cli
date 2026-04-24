"""Region/environment-tier tagging for chains (e.g. dev, staging, prod)."""

from envchain.chain import get_chain, add_chain, get_chain_names

_REGION_KEY = "__region__"
VALID_REGIONS = {"dev", "staging", "prod", "local", "test"}


class RegionError(Exception):
    pass


def set_region(chain_name: str, region: str, password: str) -> None:
    """Assign a region/tier to a chain."""
    if region not in VALID_REGIONS:
        raise RegionError(
            f"Invalid region '{region}'. Must be one of: {', '.join(sorted(VALID_REGIONS))}"
        )
    data = get_chain(chain_name, password)
    if data is None:
        raise RegionError(f"Chain '{chain_name}' not found.")
    data[_REGION_KEY] = region
    add_chain(chain_name, data, password)


def get_region(chain_name: str, password: str) -> str | None:
    """Return the region assigned to a chain, or None if unset."""
    data = get_chain(chain_name, password)
    if data is None:
        raise RegionError(f"Chain '{chain_name}' not found.")
    return data.get(_REGION_KEY)


def clear_region(chain_name: str, password: str) -> None:
    """Remove the region tag from a chain."""
    data = get_chain(chain_name, password)
    if data is None:
        raise RegionError(f"Chain '{chain_name}' not found.")
    data.pop(_REGION_KEY, None)
    add_chain(chain_name, data, password)


def list_by_region(region: str, password: str) -> list[str]:
    """Return all chain names assigned to the given region."""
    if region not in VALID_REGIONS:
        raise RegionError(
            f"Invalid region '{region}'. Must be one of: {', '.join(sorted(VALID_REGIONS))}"
        )
    results = []
    for name in get_chain_names(password):
        data = get_chain(name, password)
        if data and data.get(_REGION_KEY) == region:
            results.append(name)
    return results
