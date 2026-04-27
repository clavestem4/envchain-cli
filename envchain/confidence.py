from typing import Optional
from envchain.chain import get_chain, update_chain, get_chain_names

VALID_LEVELS = {"low", "medium", "high", "verified"}


class ConfidenceError(Exception):
    pass


def set_confidence(chain_name: str, level: str, password: str) -> None:
    """Set a confidence level on a chain."""
    if level not in VALID_LEVELS:
        raise ConfidenceError(
            f"Invalid confidence level '{level}'. Must be one of: {', '.join(sorted(VALID_LEVELS))}"
        )
    chain = get_chain(chain_name, password)
    chain["__confidence__"] = level
    update_chain(chain_name, chain, password)


def get_confidence(chain_name: str, password: str) -> Optional[str]:
    """Get the confidence level of a chain, or None if not set."""
    chain = get_chain(chain_name, password)
    return chain.get("__confidence__")


def clear_confidence(chain_name: str, password: str) -> None:
    """Remove the confidence level from a chain."""
    chain = get_chain(chain_name, password)
    if "__confidence__" not in chain:
        raise ConfidenceError(f"No confidence level set on chain '{chain_name}'")
    del chain["__confidence__"]
    update_chain(chain_name, chain, password)


def list_by_confidence(password: str, level: Optional[str] = None) -> dict:
    """Return a mapping of chain_name -> confidence level, optionally filtered."""
    result = {}
    for name in get_chain_names(password):
        chain = get_chain(name, password)
        lvl = chain.get("__confidence__")
        if lvl is not None:
            if level is None or lvl == level:
                result[name] = lvl
    return result
