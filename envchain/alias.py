"""Alias support: short names that point to existing chains."""

from envchain.chain import get_chain, add_chain, get_chain_names

_ALIAS_KEY = "__aliases__"


def _get_aliases(get_chain_fn=get_chain, get_names_fn=get_chain_names) -> dict:
    names = get_names_fn()
    if _ALIAS_KEY not in names:
        return {}
    chain = get_chain_fn(_ALIAS_KEY, "")
    return chain.get("vars", {})


def set_alias(alias: str, target: str, get_chain_fn=get_chain,
              add_chain_fn=add_chain, get_names_fn=get_chain_names) -> None:
    """Create or update an alias pointing to target chain."""
    names = get_names_fn()
    if target not in names:
        raise KeyError(f"Target chain '{target}' does not exist.")
    aliases = _get_aliases(get_chain_fn, get_names_fn)
    aliases[alias] = target
    add_chain_fn(_ALIAS_KEY, "", aliases, overwrite=True)


def remove_alias(alias: str, get_chain_fn=get_chain,
                 add_chain_fn=add_chain, get_names_fn=get_chain_names) -> None:
    """Remove an alias."""
    aliases = _get_aliases(get_chain_fn, get_names_fn)
    if alias not in aliases:
        raise KeyError(f"Alias '{alias}' does not exist.")
    del aliases[alias]
    add_chain_fn(_ALIAS_KEY, "", aliases, overwrite=True)


def resolve_alias(alias: str, get_chain_fn=get_chain,
                  get_names_fn=get_chain_names) -> str:
    """Return the target chain name for an alias, or the input if not an alias."""
    aliases = _get_aliases(get_chain_fn, get_names_fn)
    return aliases.get(alias, alias)


def list_aliases(get_chain_fn=get_chain,
                 get_names_fn=get_chain_names) -> dict:
    """Return all alias -> target mappings."""
    return dict(_get_aliases(get_chain_fn, get_names_fn))
