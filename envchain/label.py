"""Label support for chains — attach arbitrary key/value metadata labels."""

from envchain.chain import get_chain, add_chain, get_chain_names

LABELS_KEY = "__labels__"


class LabelError(Exception):
    pass


def _get_labels(chain: dict) -> dict:
    raw = chain.get(LABELS_KEY, "")
    if not raw:
        return {}
    result = {}
    for pair in raw.split(","):
        if "=" in pair:
            k, v = pair.split("=", 1)
            result[k.strip()] = v.strip()
    return result


def set_label(chain_name: str, key: str, value: str, password: str) -> None:
    chain = get_chain(chain_name, password)
    labels = _get_labels(chain)
    labels[key] = value
    chain[LABELS_KEY] = ",".join(f"{k}={v}" for k, v in labels.items())
    add_chain(chain_name, chain, password, overwrite=True)


def remove_label(chain_name: str, key: str, password: str) -> None:
    chain = get_chain(chain_name, password)
    labels = _get_labels(chain)
    if key not in labels:
        raise LabelError(f"Label '{key}' not found on chain '{chain_name}'.")
    del labels[key]
    chain[LABELS_KEY] = ",".join(f"{k}={v}" for k, v in labels.items())
    add_chain(chain_name, chain, password, overwrite=True)


def get_labels(chain_name: str, password: str) -> dict:
    chain = get_chain(chain_name, password)
    return _get_labels(chain)


def find_by_label(key: str, value: str, password: str) -> list[str]:
    matches = []
    for name in get_chain_names(password):
        try:
            chain = get_chain(name, password)
            labels = _get_labels(chain)
            if labels.get(key) == value:
                matches.append(name)
        except Exception:
            pass
    return matches
