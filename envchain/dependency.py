"""Chain dependency tracking — define which chains must exist before another."""

from typing import List, Dict
from envchain.chain import get_chain, add_chain, get_chain_names


class DependencyError(Exception):
    pass


def _get_deps(chain: dict) -> List[str]:
    return chain.get("__meta__", {}).get("depends_on", [])


def set_dependencies(name: str, deps: List[str], password: str) -> None:
    chain = get_chain(name, password)
    for dep in deps:
        if dep not in get_chain_names(password):
            raise DependencyError(f"Dependency '{dep}' does not exist.")
        if dep == name:
            raise DependencyError("A chain cannot depend on itself.")
    meta = chain.get("__meta__", {})
    meta["depends_on"] = deps
    chain["__meta__"] = meta
    add_chain(name, chain, password, overwrite=True)


def get_dependencies(name: str, password: str) -> List[str]:
    chain = get_chain(name, password)
    return _get_deps(chain)


def clear_dependencies(name: str, password: str) -> None:
    chain = get_chain(name, password)
    meta = chain.get("__meta__", {})
    meta.pop("depends_on", None)
    chain["__meta__"] = meta
    add_chain(name, chain, password, overwrite=True)


def resolve_order(names: List[str], password: str) -> List[str]:
    """Topological sort of chains by dependency order."""
    visited: Dict[str, bool] = {}
    order: List[str] = []

    def visit(n: str, stack: List[str]) -> None:
        if n in stack:
            raise DependencyError(f"Circular dependency detected: {' -> '.join(stack + [n])}")
        if visited.get(n):
            return
        stack.append(n)
        for dep in get_dependencies(n, password):
            visit(dep, stack)
        stack.pop()
        visited[n] = True
        order.append(n)

    for name in names:
        visit(name, [])
    return order
