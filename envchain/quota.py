"""Quota management: enforce max variable counts per chain."""

from envchain.chain import get_chain, add_chain, get_chain_names

QUOTA_META_KEY = "__quota__"
DEFAULT_QUOTA = None  # None means unlimited


class QuotaError(Exception):
    pass


def set_quota(chain_name: str, max_vars: int, password: str) -> None:
    """Set the maximum number of variables allowed in a chain."""
    if max_vars < 1:
        raise QuotaError(f"Quota must be at least 1, got {max_vars}")
    chain = get_chain(chain_name, password)
    chain[QUOTA_META_KEY] = str(max_vars)
    add_chain(chain_name, chain, password, overwrite=True)


def get_quota(chain_name: str, password: str) -> int | None:
    """Return the quota for a chain, or None if unlimited."""
    chain = get_chain(chain_name, password)
    raw = chain.get(QUOTA_META_KEY)
    return int(raw) if raw is not None else DEFAULT_QUOTA


def clear_quota(chain_name: str, password: str) -> None:
    """Remove quota limit from a chain."""
    chain = get_chain(chain_name, password)
    if QUOTA_META_KEY in chain:
        del chain[QUOTA_META_KEY]
        add_chain(chain_name, chain, password, overwrite=True)


def check_quota(chain_name: str, password: str) -> dict:
    """Return a dict with quota info: limit, used, remaining, exceeded."""
    chain = get_chain(chain_name, password)
    quota = int(chain[QUOTA_META_KEY]) if QUOTA_META_KEY in chain else DEFAULT_QUOTA
    used = len([k for k in chain if not k.startswith("__")])
    if quota is None:
        return {"limit": None, "used": used, "remaining": None, "exceeded": False}
    remaining = quota - used
    return {
        "limit": quota,
        "used": used,
        "remaining": remaining,
        "exceeded": remaining < 0,
    }


def list_over_quota(password: str) -> list[str]:
    """Return names of chains that exceed their quota."""
    over = []
    for name in get_chain_names(password):
        try:
            info = check_quota(name, password)
            if info["exceeded"]:
                over.append(name)
        except Exception:
            continue
    return over
