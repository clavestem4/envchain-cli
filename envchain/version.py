"""Version tracking and compatibility metadata for envchain chains."""

from datetime import datetime, timezone
from envchain.chain import get_chain, add_chain, get_chain_names

VERSION_KEY = "__version__"
CREATED_KEY = "__created_at__"
UPDATED_KEY = "__updated_at__"


class VersionError(Exception):
    pass


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def stamp_chain(chain_name: str, password: str) -> None:
    """Add or update version metadata on a chain."""
    try:
        chain = get_chain(chain_name, password)
    except Exception as e:
        raise VersionError(f"Chain '{chain_name}' not found: {e}")

    now = _now_iso()
    if VERSION_KEY not in chain:
        chain[CREATED_KEY] = now
        chain[VERSION_KEY] = "1"
    else:
        chain[VERSION_KEY] = str(int(chain[VERSION_KEY]) + 1)

    chain[UPDATED_KEY] = now
    add_chain(chain_name, chain, password, overwrite=True)


def get_version_info(chain_name: str, password: str) -> dict:
    """Return version metadata for a chain."""
    try:
        chain = get_chain(chain_name, password)
    except Exception as e:
        raise VersionError(f"Chain '{chain_name}' not found: {e}")

    return {
        "chain": chain_name,
        "version": chain.get(VERSION_KEY),
        "created_at": chain.get(CREATED_KEY),
        "updated_at": chain.get(UPDATED_KEY),
    }


def list_versioned_chains(password: str) -> list:
    """Return names of chains that have version metadata."""
    names = get_chain_names(password)
    versioned = []
    for name in names:
        try:
            chain = get_chain(name, password)
            if VERSION_KEY in chain:
                versioned.append(name)
        except Exception:
            continue
    return versioned
