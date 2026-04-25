"""Compliance tagging for chains — mark chains with compliance standards (e.g. SOC2, HIPAA, PCI)."""

from typing import Optional
from envchain.chain import get_chain, add_chain, get_chain_names

VALID_STANDARDS = {"SOC2", "HIPAA", "PCI", "GDPR", "ISO27001", "NIST", "CUSTOM"}
_META_KEY = "__compliance__"


class ComplianceError(Exception):
    pass


def _get_compliance(chain: dict) -> dict:
    raw = chain.get(_META_KEY)
    if isinstance(raw, dict):
        return raw
    return {}


def set_compliance(
    chain_name: str,
    standard: str,
    note: Optional[str] = None,
    password: str = "",
    get_chain_fn=get_chain,
    add_chain_fn=add_chain,
) -> None:
    """Tag a chain with a compliance standard."""
    if standard not in VALID_STANDARDS:
        raise ComplianceError(
            f"Unknown standard '{standard}'. Valid: {sorted(VALID_STANDARDS)}"
        )
    chain = get_chain_fn(chain_name, password)
    compliance = _get_compliance(chain)
    compliance[standard] = {"note": note or ""}
    chain[_META_KEY] = compliance
    add_chain_fn(chain_name, chain, password, overwrite=True)


def remove_compliance(
    chain_name: str,
    standard: str,
    password: str = "",
    get_chain_fn=get_chain,
    add_chain_fn=add_chain,
) -> None:
    """Remove a compliance standard tag from a chain."""
    chain = get_chain_fn(chain_name, password)
    compliance = _get_compliance(chain)
    if standard not in compliance:
        raise ComplianceError(f"Standard '{standard}' not set on '{chain_name}'.")
    del compliance[standard]
    chain[_META_KEY] = compliance
    add_chain_fn(chain_name, chain, password, overwrite=True)


def get_compliance(
    chain_name: str,
    password: str = "",
    get_chain_fn=get_chain,
) -> dict:
    """Return all compliance tags for a chain."""
    chain = get_chain_fn(chain_name, password)
    return _get_compliance(chain)


def list_by_compliance(
    standard: str,
    password: str = "",
    get_chain_names_fn=get_chain_names,
    get_chain_fn=get_chain,
) -> list:
    """Return all chain names tagged with the given compliance standard."""
    results = []
    for name in get_chain_names_fn():
        try:
            chain = get_chain_fn(name, password)
            if standard in _get_compliance(chain):
                results.append(name)
        except Exception:
            continue
    return results
