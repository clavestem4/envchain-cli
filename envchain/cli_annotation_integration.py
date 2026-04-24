"""Integration helpers for annotation-aware chain operations."""

from typing import Optional
from envchain.annotation import get_annotations, find_by_annotation
from envchain.chain import get_chain, get_chain_names


def annotated_chain_summary(chain_name: str, password: str) -> dict:
    """Return a dict with chain vars and its annotations merged for display."""
    chain = get_chain(chain_name, password)
    annotations = get_annotations(chain_name, password)
    vars_only = {k: v for k, v in chain.items() if not k.startswith("__")}
    return {
        "name": chain_name,
        "vars": vars_only,
        "annotations": annotations,
    }


def chains_with_annotation(
    key: str,
    value: Optional[str],
    password: str,
) -> list:
    """Return full summaries of chains matching an annotation filter."""
    names = find_by_annotation(key, value, get_chain_names, password)
    return [annotated_chain_summary(n, password) for n in names]


def annotation_index(password: str) -> dict:
    """Build an index mapping annotation keys to lists of chain names."""
    index: dict = {}
    for name in get_chain_names(password):
        try:
            annotations = get_annotations(name, password)
            for k in annotations:
                index.setdefault(k, []).append(name)
        except Exception:
            continue
    return index
