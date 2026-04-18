"""Tag management for envchain chains."""
from envchain.chain import get_chain, add_chain, get_chain_names

TAGS_KEY = "__tags__"


def add_tag(chain_name: str, tag: str, password: str) -> None:
    """Add a tag to a chain."""
    chain = get_chain(chain_name, password)
    tags = _get_tags(chain)
    if tag not in tags:
        tags.append(tag)
    chain[TAGS_KEY] = ",".join(tags)
    add_chain(chain_name, chain, password, overwrite=True)


def remove_tag(chain_name: str, tag: str, password: str) -> None:
    """Remove a tag from a chain."""
    chain = get_chain(chain_name, password)
    tags = _get_tags(chain)
    tags = [t for t in tags if t != tag]
    chain[TAGS_KEY] = ",".join(tags)
    add_chain(chain_name, chain, password, overwrite=True)


def get_tags(chain_name: str, password: str) -> list[str]:
    """Return tags for a chain."""
    chain = get_chain(chain_name, password)
    return _get_tags(chain)


def find_by_tag(tag: str, password: str) -> list[str]:
    """Return chain names that have the given tag."""
    results = []
    for name in get_chain_names(password):
        try:
            chain = get_chain(name, password)
            if tag in _get_tags(chain):
                results.append(name)
        except Exception:
            continue
    return results


def _get_tags(chain: dict) -> list[str]:
    raw = chain.get(TAGS_KEY, "")
    return [t for t in raw.split(",") if t]
