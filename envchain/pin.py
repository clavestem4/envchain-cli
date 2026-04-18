"""Pin/favorite chains for quick access."""
from envchain.chain import get_chain, get_chain_names, add_chain

_PINS_CHAIN = "__pins__"


def _get_pins(get_chain_fn=get_chain) -> list:
    try:
        chain = get_chain_fn(_PINS_CHAIN)
        return list(chain.get("pins", {}).keys())
    except KeyError:
        return []


def pin_chain(name: str, get_chain_fn=get_chain, add_chain_fn=add_chain) -> None:
    if name.startswith("__"):
        raise ValueError(f"Cannot pin internal chain: {name}")
    try:
        get_chain_fn(name)
    except KeyError:
        raise KeyError(f"Chain '{name}' does not exist")
    pins = _get_pins(get_chain_fn)
    if name in pins:
        return
    pins.append(name)
    add_chain_fn(_PINS_CHAIN, {p: "1" for p in pins}, overwrite=True)


def unpin_chain(name: str, get_chain_fn=get_chain, add_chain_fn=add_chain) -> None:
    pins = _get_pins(get_chain_fn)
    if name not in pins:
        raise KeyError(f"Chain '{name}' is not pinned")
    pins.remove(name)
    add_chain_fn(_PINS_CHAIN, {p: "1" for p in pins}, overwrite=True)


def get_pinned(get_chain_fn=get_chain) -> list:
    return _get_pins(get_chain_fn)


def is_pinned(name: str, get_chain_fn=get_chain) -> bool:
    return name in _get_pins(get_chain_fn)
