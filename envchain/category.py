from typing import Optional
from envchain.chain import get_chain, add_chain, get_chain_names

CATEGORY_KEY = "__category__"


class CategoryError(Exception):
    pass


def set_category(chain_name: str, category: str, password: str) -> None:
    chain = get_chain(chain_name, password)
    if chain is None:
        raise CategoryError(f"Chain '{chain_name}' not found.")
    chain[CATEGORY_KEY] = category
    add_chain(chain_name, chain, password, overwrite=True)


def get_category(chain_name: str, password: str) -> Optional[str]:
    chain = get_chain(chain_name, password)
    if chain is None:
        raise CategoryError(f"Chain '{chain_name}' not found.")
    return chain.get(CATEGORY_KEY)


def clear_category(chain_name: str, password: str) -> None:
    chain = get_chain(chain_name, password)
    if chain is None:
        raise CategoryError(f"Chain '{chain_name}' not found.")
    chain.pop(CATEGORY_KEY, None)
    add_chain(chain_name, chain, password, overwrite=True)


def list_by_category(category: str, password: str) -> list[str]:
    results = []
    for name in get_chain_names(password):
        try:
            chain = get_chain(name, password)
            if chain and chain.get(CATEGORY_KEY) == category:
                results.append(name)
        except Exception:
            continue
    return results


def list_all_categories(password: str) -> dict[str, list[str]]:
    categories: dict[str, list[str]] = {}
    for name in get_chain_names(password):
        try:
            chain = get_chain(name, password)
            if chain:
                cat = chain.get(CATEGORY_KEY)
                if cat:
                    categories.setdefault(cat, []).append(name)
        except Exception:
            continue
    return categories
