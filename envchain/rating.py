"""Chain rating/scoring module for envchain."""

from envchain.chain import get_chain, add_chain, get_chain_names

RATING_KEY = "__rating__"
VALID_RATINGS = {1, 2, 3, 4, 5}


class RatingError(Exception):
    pass


def set_rating(chain_name: str, rating: int, password: str) -> None:
    """Set a numeric rating (1-5) for a chain."""
    if rating not in VALID_RATINGS:
        raise RatingError(f"Rating must be between 1 and 5, got {rating}")
    chain = get_chain(chain_name, password)
    chain[RATING_KEY] = str(rating)
    add_chain(chain_name, chain, password, overwrite=True)


def get_rating(chain_name: str, password: str) -> int | None:
    """Get the rating for a chain, or None if unset."""
    chain = get_chain(chain_name, password)
    val = chain.get(RATING_KEY)
    return int(val) if val is not None else None


def clear_rating(chain_name: str, password: str) -> None:
    """Remove the rating from a chain."""
    chain = get_chain(chain_name, password)
    if RATING_KEY not in chain:
        raise RatingError(f"Chain '{chain_name}' has no rating set")
    del chain[RATING_KEY]
    add_chain(chain_name, chain, password, overwrite=True)


def list_by_rating(password: str, min_rating: int = 1) -> list[tuple[str, int]]:
    """Return list of (chain_name, rating) sorted by rating descending."""
    results = []
    for name in get_chain_names(password):
        try:
            r = get_rating(name, password)
            if r is not None and r >= min_rating:
                results.append((name, r))
        except Exception:
            continue
    return sorted(results, key=lambda x: x[1], reverse=True)
