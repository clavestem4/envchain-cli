"""Bookmark frequently used chains for quick access."""

from envchain.chain import get_chain, get_chain_names

BOOKMARK_KEY = "__bookmarks__"


class BookmarkError(Exception):
    pass


def _get_bookmarks(get_fn, add_fn):
    try:
        chain = get_fn(BOOKMARK_KEY)
        return chain.get("chains", [])
    except Exception:
        return []


def add_bookmark(name: str, get_fn=None, add_fn=None):
    from envchain.chain import get_chain, add_chain
    get_fn = get_fn or get_chain
    add_fn = add_fn or add_chain

    names = get_chain_names() if get_fn is get_chain else []
    try:
        get_fn(name)
    except Exception:
        raise BookmarkError(f"Chain '{name}' does not exist.")

    bookmarks = _get_bookmarks(get_fn, add_fn)
    if name in bookmarks:
        return  # already bookmarked
    bookmarks.append(name)
    add_fn(BOOKMARK_KEY, {"chains": bookmarks}, overwrite=True)


def remove_bookmark(name: str, get_fn=None, add_fn=None):
    from envchain.chain import add_chain
    get_fn = get_fn or get_chain
    add_fn = add_fn or add_chain

    bookmarks = _get_bookmarks(get_fn, add_fn)
    if name not in bookmarks:
        raise BookmarkError(f"'{name}' is not bookmarked.")
    bookmarks.remove(name)
    add_fn(BOOKMARK_KEY, {"chains": bookmarks}, overwrite=True)


def get_bookmarks(get_fn=None, add_fn=None):
    from envchain.chain import add_chain
    get_fn = get_fn or get_chain
    add_fn = add_fn or add_chain
    return _get_bookmarks(get_fn, add_fn)


def is_bookmarked(name: str, get_fn=None, add_fn=None):
    return name in get_bookmarks(get_fn, add_fn)
