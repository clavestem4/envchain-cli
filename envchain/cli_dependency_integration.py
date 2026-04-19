"""Higher-level dependency utilities used by other CLI commands."""

from typing import List, Dict
from envchain.dependency import get_dependencies, resolve_order, DependencyError
from envchain.chain import get_chain, get_chain_names


def load_chain_with_deps(name: str, password: str) -> Dict[str, dict]:
    """Return an ordered dict of {chain_name: vars} respecting dependency order."""
    all_names = _collect_all_deps(name, password)
    order = resolve_order(all_names, password)
    return {n: get_chain(n, password) for n in order}


def _collect_all_deps(name: str, password: str, seen=None) -> List[str]:
    if seen is None:
        seen = set()
    if name in seen:
        return []
    seen.add(name)
    result = [name]
    for dep in get_dependencies(name, password):
        result.extend(_collect_all_deps(dep, password, seen))
    return result


def dependency_tree(name: str, password: str, indent: int = 0) -> str:
    """Return a human-readable dependency tree string."""
    lines = ["  " * indent + name]
    for dep in get_dependencies(name, password):
        lines.append(dependency_tree(dep, password, indent + 1))
    return "\n".join(lines)


def find_dependents(target: str, password: str) -> List[str]:
    """Find all chains that depend (directly) on the given chain."""
    result = []
    for name in get_chain_names(password):
        if target in get_dependencies(name, password):
            result.append(name)
    return result
