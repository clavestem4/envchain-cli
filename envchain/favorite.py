"""Favorite chains — quickly mark and retrieve frequently used chains."""

from envchain.chain import get_chain, get_chain_names, add_chain


class FavoriteError(Exception):
    pass


FAVORITES_KEY = "__favorites__"


def _get_favorites(get_chain_fn, get_names_fn):
    names = get_names_fn()
    if FAVORITES_KEY not in names:
        return []
    chain = get_chain_fn(FAVORITES_KEY)
    return list(chain.get("chains", {}).keys())


def add_favorite(name, password, get_chain_fn=get_chain, get_names_fn=get_chain_names, add_chain_fn=add_chain):
    names = get_names_fn()
    if name not in names:
        raise FavoriteError(f"Chain '{name}' does not exist.")
    favorites = _get_favorites(get_chain_fn, get_names_fn)
    if name in favorites:
        return  # already favorited
    favorites.append(name)
    payload = {k: "1" for k in favorites}
    add_chain_fn(FAVORITES_KEY, payload, password)


def remove_favorite(name, password, get_chain_fn=get_chain, get_names_fn=get_chain_names, add_chain_fn=add_chain):
    favorites = _get_favorites(get_chain_fn, get_names_fn)
    if name not in favorites:
        raise FavoriteError(f"Chain '{name}' is not a favorite.")
    favorites.remove(name)
    payload = {k: "1" for k in favorites}
    add_chain_fn(FAVORITES_KEY, payload, password)


def get_favorites(get_chain_fn=get_chain, get_names_fn=get_chain_names):
    return _get_favorites(get_chain_fn, get_names_fn)


def is_favorite(name, get_chain_fn=get_chain, get_names_fn=get_chain_names):
    return name in _get_favorites(get_chain_fn, get_names_fn)
