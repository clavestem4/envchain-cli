"""Provenance tracking for envchain chains.

Records the origin and source metadata of a chain — where it came from,
how it was created, and any upstream references.
"""

from __future__ import annotations

from typing import Optional

from envchain.chain import get_chain, update_chain, get_chain_names

META_KEY = "__provenance__"

VALID_SOURCES = {"manual", "import", "clone", "template", "merge", "snapshot", "external"}


class ProvenanceError(Exception):
    """Raised when a provenance operation fails."""


def _get_provenance(chain: dict) -> dict:
    """Extract provenance metadata from a chain dict."""
    return chain.get(META_KEY, {})


def set_provenance(
    chain_name: str,
    source: str,
    password: str,
    origin: Optional[str] = None,
    notes: Optional[str] = None,
    get_fn=get_chain,
    update_fn=update_chain,
) -> None:
    """Set provenance metadata on a chain.

    Args:
        chain_name: Name of the chain to update.
        source: Source type (e.g. 'manual', 'import', 'clone').
        password: Encryption password.
        origin: Optional free-form origin reference (URL, path, chain name, etc.).
        notes: Optional human-readable notes about provenance.
        get_fn: Dependency-injectable get_chain function.
        update_fn: Dependency-injectable update_chain function.

    Raises:
        ProvenanceError: If the chain does not exist or source is invalid.
    """
    if source not in VALID_SOURCES:
        raise ProvenanceError(
            f"Invalid source '{source}'. Must be one of: {', '.join(sorted(VALID_SOURCES))}"
        )

    try:
        chain = get_fn(chain_name, password)
    except KeyError:
        raise ProvenanceError(f"Chain '{chain_name}' not found.")

    provenance: dict = {
        "source": source,
    }
    if origin is not None:
        provenance["origin"] = origin
    if notes is not None:
        provenance["notes"] = notes

    chain[META_KEY] = provenance
    update_fn(chain_name, chain, password)


def get_provenance(
    chain_name: str,
    password: str,
    get_fn=get_chain,
) -> Optional[dict]:
    """Retrieve provenance metadata for a chain.

    Returns:
        A dict with provenance fields, or None if not set.

    Raises:
        ProvenanceError: If the chain does not exist.
    """
    try:
        chain = get_fn(chain_name, password)
    except KeyError:
        raise ProvenanceError(f"Chain '{chain_name}' not found.")

    prov = _get_provenance(chain)
    return prov if prov else None


def clear_provenance(
    chain_name: str,
    password: str,
    get_fn=get_chain,
    update_fn=update_chain,
) -> None:
    """Remove provenance metadata from a chain.

    Raises:
        ProvenanceError: If the chain does not exist.
    """
    try:
        chain = get_fn(chain_name, password)
    except KeyError:
        raise ProvenanceError(f"Chain '{chain_name}' not found.")

    chain.pop(META_KEY, None)
    update_fn(chain_name, chain, password)


def list_by_source(
    source: str,
    password: str,
    names_fn=get_chain_names,
    get_fn=get_chain,
) -> list[str]:
    """Return all chain names whose provenance source matches the given value.

    Args:
        source: The source type to filter by.
        password: Encryption password.
        names_fn: Dependency-injectable get_chain_names function.
        get_fn: Dependency-injectable get_chain function.

    Returns:
        Sorted list of matching chain names.
    """
    results = []
    for name in names_fn():
        try:
            chain = get_fn(name, password)
        except Exception:
            continue
        prov = _get_provenance(chain)
        if prov.get("source") == source:
            results.append(name)
    return sorted(results)
