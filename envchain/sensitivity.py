from __future__ import annotations

VALID_LEVELS = {"public", "internal", "confidential", "secret", "top-secret"}

_META_KEY = "__sensitivity__"


class SensitivityError(Exception):
    pass


def set_sensitivity(
    chain_name: str,
    level: str,
    password: str,
    get_chain_fn,
    add_chain_fn,
) -> None:
    if level not in VALID_LEVELS:
        raise SensitivityError(
            f"Invalid sensitivity level '{level}'. "
            f"Valid levels: {', '.join(sorted(VALID_LEVELS))}"
        )
    try:
        data = get_chain_fn(chain_name, password)
    except KeyError:
        raise SensitivityError(f"Chain '{chain_name}' not found.")
    data[_META_KEY] = level
    add_chain_fn(chain_name, password, data)


def get_sensitivity(
    chain_name: str,
    password: str,
    get_chain_fn,
) -> str | None:
    try:
        data = get_chain_fn(chain_name, password)
    except KeyError:
        raise SensitivityError(f"Chain '{chain_name}' not found.")
    return data.get(_META_KEY)


def clear_sensitivity(
    chain_name: str,
    password: str,
    get_chain_fn,
    add_chain_fn,
) -> None:
    try:
        data = get_chain_fn(chain_name, password)
    except KeyError:
        raise SensitivityError(f"Chain '{chain_name}' not found.")
    data.pop(_META_KEY, None)
    add_chain_fn(chain_name, password, data)


def list_by_sensitivity(
    level: str,
    password: str,
    get_chain_names_fn,
    get_chain_fn,
) -> list[str]:
    if level not in VALID_LEVELS:
        raise SensitivityError(
            f"Invalid sensitivity level '{level}'. "
            f"Valid levels: {', '.join(sorted(VALID_LEVELS))}"
        )
    result = []
    for name in get_chain_names_fn():
        try:
            data = get_chain_fn(name, password)
        except Exception:
            continue
        if data.get(_META_KEY) == level:
            result.append(name)
    return result
