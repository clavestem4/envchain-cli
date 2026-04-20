"""Namespace support for grouping chains under a dotted prefix (e.g. 'prod.api')."""

from envchain.chain import get_chain, get_chain_names


class NamespaceError(Exception):
    pass


SEP = "."


def _validate_namespace(ns: str) -> None:
    if not ns or SEP in ns.strip(SEP):
        raise NamespaceError(f"Invalid namespace '{ns}': must be a single non-empty segment.")
    if not ns.replace("_", "").replace("-", "").isalnum():
        raise NamespaceError(
            f"Invalid namespace '{ns}': only alphanumeric, hyphen, and underscore allowed."
        )


def qualify(namespace: str, chain_name: str) -> str:
    """Return the fully-qualified chain name: '<namespace>.<chain_name>'."""
    _validate_namespace(namespace)
    return f"{namespace}{SEP}{chain_name}"


def split_qualified(name: str):
    """Split a qualified name into (namespace, chain_name). Returns (None, name) if no namespace."""
    if SEP in name:
        ns, _, chain = name.partition(SEP)
        return ns, chain
    return None, name


def list_in_namespace(namespace: str, password: str) -> list:
    """Return all chain names that belong to the given namespace."""
    _validate_namespace(namespace)
    prefix = f"{namespace}{SEP}"
    return [n for n in get_chain_names(password) if n.startswith(prefix)]


def get_namespaces(password: str) -> list:
    """Return a sorted list of all distinct namespaces in use."""
    namespaces = set()
    for name in get_chain_names(password):
        ns, _ = split_qualified(name)
        if ns:
            namespaces.add(ns)
    return sorted(namespaces)


def get_chains_in_namespace(namespace: str, password: str) -> dict:
    """Return a dict of {short_name: chain_data} for all chains under the namespace."""
    _validate_namespace(namespace)
    result = {}
    for fqn in list_in_namespace(namespace, password):
        _, short = split_qualified(fqn)
        result[short] = get_chain(fqn, password)
    return result
