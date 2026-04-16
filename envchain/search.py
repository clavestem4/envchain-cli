"""Search/filter utilities for envchain chains and variables."""
from typing import Optional
from envchain.chain import get_chain_names, get_chain


def search_chains(password: str, query: str, store_path: Optional[str] = None) -> list[dict]:
    """Search chains by name, returning matching chain names and their variable keys."""
    kwargs = {"store_path": store_path} if store_path else {}
    names = get_chain_names(password, **kwargs)
    query_lower = query.lower()
    results = []
    for name in names:
        if query_lower in name.lower():
            chain = get_chain(name, password, **kwargs)
            results.append({"chain": name, "vars": list(chain.keys()), "match": "name"})
    return results


def search_variables(password: str, query: str, store_path: Optional[str] = None) -> list[dict]:
    """Search for variable keys matching query across all chains."""
    kwargs = {"store_path": store_path} if store_path else {}
    names = get_chain_names(password, **kwargs)
    query_lower = query.lower()
    results = []
    for name in names:
        chain = get_chain(name, password, **kwargs)
        matched_keys = [k for k in chain.keys() if query_lower in k.lower()]
        if matched_keys:
            results.append({"chain": name, "vars": matched_keys, "match": "variable"})
    return results


def search_all(password: str, query: str, store_path: Optional[str] = None) -> list[dict]:
    """Search both chain names and variable keys, merging results."""
    kwargs = {"store_path": store_path} if store_path else {}
    names = get_chain_names(password, **kwargs)
    query_lower = query.lower()
    results = []
    for name in names:
        chain = get_chain(name, password, **kwargs)
        name_match = query_lower in name.lower()
        matched_keys = [k for k in chain.keys() if query_lower in k.lower()]
        if name_match or matched_keys:
            match_type = "both" if name_match and matched_keys else ("name" if name_match else "variable")
            display_keys = list(chain.keys()) if name_match else matched_keys
            results.append({"chain": name, "vars": display_keys, "match": match_type})
    return results
