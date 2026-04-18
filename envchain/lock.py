"""Chain locking — prevent accidental writes to a chain."""

from envchain.chain import get_chain, add_chain, get_chain_names

_LOCK_KEY = "__locked__"


def lock_chain(chain_name: str, password: str) -> None:
    """Lock a chain to prevent modifications."""
    chain = get_chain(chain_name, password)
    if chain.get(_LOCK_KEY) == "true":
        raise ValueError(f"Chain '{chain_name}' is already locked.")
    chain[_LOCK_KEY] = "true"
    add_chain(chain_name, chain, password, overwrite=True)


def unlock_chain(chain_name: str, password: str) -> None:
    """Unlock a chain to allow modifications."""
    chain = get_chain(chain_name, password)
    if chain.get(_LOCK_KEY) != "true":
        raise ValueError(f"Chain '{chain_name}' is not locked.")
    chain.pop(_LOCK_KEY)
    add_chain(chain_name, chain, password, overwrite=True)


def is_locked(chain_name: str, password: str) -> bool:
    """Return True if the chain is locked."""
    chain = get_chain(chain_name, password)
    return chain.get(_LOCK_KEY) == "true"


def list_locked(password: str) -> list[str]:
    """Return names of all locked chains."""
    locked = []
    for name in get_chain_names():
        try:
            if is_locked(name, password):
                locked.append(name)
        except Exception:
            continue
    return locked
