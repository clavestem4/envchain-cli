"""Chain status: active, inactive, archived."""

from envchain.chain import get_chain, add_chain, get_chain_names

VALID_STATUSES = {"active", "inactive", "archived"}
STATUS_KEY = "__status__"


class StatusError(Exception):
    pass


def set_status(chain_name: str, status: str, password: str) -> None:
    if status not in VALID_STATUSES:
        raise StatusError(f"Invalid status '{status}'. Choose from: {', '.join(sorted(VALID_STATUSES))}")
    chain = get_chain(chain_name, password)
    chain[STATUS_KEY] = status
    add_chain(chain_name, chain, password, overwrite=True)


def get_status(chain_name: str, password: str) -> str:
    chain = get_chain(chain_name, password)
    return chain.get(STATUS_KEY, "active")


def clear_status(chain_name: str, password: str) -> None:
    chain = get_chain(chain_name, password)
    chain.pop(STATUS_KEY, None)
    add_chain(chain_name, chain, password, overwrite=True)


def list_by_status(status: str, password: str) -> list[str]:
    if status not in VALID_STATUSES:
        raise StatusError(f"Invalid status '{status}'.")
    results = []
    for name in get_chain_names(password):
        try:
            if get_status(name, password) == status:
                results.append(name)
        except Exception:
            continue
    return results
