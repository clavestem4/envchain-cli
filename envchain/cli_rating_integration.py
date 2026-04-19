"""Integration helpers for rating-aware chain operations."""

from envchain.rating import list_by_rating, get_rating
from envchain.chain import get_chain


def get_top_rated_chains(password: str, top_n: int = 5) -> list[tuple[str, int]]:
    """Return the top N rated chains."""
    rated = list_by_rating(password)
    return rated[:top_n]


def get_chains_with_vars_by_rating(
    password: str, min_rating: int = 1
) -> list[tuple[str, int, dict]]:
    """
    Return list of (chain_name, rating, vars_dict) for chains
    meeting the minimum rating, sorted by rating descending.
    Excludes internal rating key from returned vars.
    """
    from envchain.rating import RATING_KEY

    results = []
    for name, rating in list_by_rating(password, min_rating=min_rating):
        try:
            chain = get_chain(name, password)
            clean = {k: v for k, v in chain.items() if k != RATING_KEY}
            results.append((name, rating, clean))
        except Exception:
            continue
    return results


def summarize_ratings(password: str) -> dict:
    """Return a summary dict with count, average, and top chain."""
    rated = list_by_rating(password)
    if not rated:
        return {"count": 0, "average": None, "top": None}
    total = sum(r for _, r in rated)
    avg = round(total / len(rated), 2)
    top = rated[0][0]
    return {"count": len(rated), "average": avg, "top": top}
