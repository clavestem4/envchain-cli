"""Annotation support for chains — attach freeform key-value metadata."""

from typing import Optional
from envchain.chain import get_chain, add_chain

ANNOTATION_KEY = "__annotations__"


class AnnotationError(Exception):
    pass


def _get_annotations(chain: dict) -> dict:
    raw = chain.get(ANNOTATION_KEY, "")
    if not raw:
        return {}
    result = {}
    for part in raw.split(";"):
        if "=" in part:
            k, _, v = part.partition("=")
            result[k.strip()] = v.strip()
    return result


def set_annotation(chain_name: str, key: str, value: str, password: str) -> None:
    """Set an annotation key-value on the given chain."""
    chain = get_chain(chain_name, password)
    annotations = _get_annotations(chain)
    annotations[key] = value
    chain[ANNOTATION_KEY] = ";".join(f"{k}={v}" for k, v in annotations.items())
    add_chain(chain_name, chain, password, overwrite=True)


def remove_annotation(chain_name: str, key: str, password: str) -> None:
    """Remove an annotation key from the given chain."""
    chain = get_chain(chain_name, password)
    annotations = _get_annotations(chain)
    if key not in annotations:
        raise AnnotationError(f"Annotation '{key}' not found on chain '{chain_name}'.")
    del annotations[key]
    chain[ANNOTATION_KEY] = ";".join(f"{k}={v}" for k, v in annotations.items())
    add_chain(chain_name, chain, password, overwrite=True)


def get_annotations(chain_name: str, password: str) -> dict:
    """Return all annotations for a chain."""
    chain = get_chain(chain_name, password)
    return _get_annotations(chain)


def find_by_annotation(
    key: str,
    value: Optional[str],
    get_chain_names,
    password: str,
) -> list:
    """Find chains that have a given annotation key (and optionally value)."""
    matches = []
    for name in get_chain_names(password):
        try:
            chain = get_chain(name, password)
            annotations = _get_annotations(chain)
            if key in annotations:
                if value is None or annotations[key] == value:
                    matches.append(name)
        except Exception:
            continue
    return matches
