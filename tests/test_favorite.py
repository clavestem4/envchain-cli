"""Tests for envchain.favorite."""

import pytest
from envchain.favorite import add_favorite, remove_favorite, get_favorites, is_favorite, FavoriteError, FAVORITES_KEY


def _make_fns(store=None):
    if store is None:
        store = {}

    def fake_get(name):
        if name not in store:
            raise KeyError(name)
        return store[name]

    def fake_add(name, vars_, password):
        store[name] = {"chains": {k: v for k, v in vars_.items()}}
        # also mirror at top level for _get_favorites key lookup
        store[name] = vars_

    def fake_names():
        return list(store.keys())

    return fake_get, fake_add, fake_names, store


def test_add_favorite_success():
    fake_get, fake_add, fake_names, store = _make_fns({"mychain": {"A": "1"}})
    add_favorite("mychain", "pass", fake_get, fake_names, fake_add)
    assert FAVORITES_KEY in store
    assert "mychain" in store[FAVORITES_KEY]


def test_add_favorite_missing_chain_raises():
    fake_get, fake_add, fake_names, store = _make_fns()
    with pytest.raises(FavoriteError):
        add_favorite("ghost", "pass", fake_get, fake_names, fake_add)


def test_add_favorite_idempotent():
    fake_get, fake_add, fake_names, store = _make_fns({"mychain": {"A": "1"}})
    add_favorite("mychain", "pass", fake_get, fake_names, fake_add)
    add_favorite("mychain", "pass", fake_get, fake_names, fake_add)
    favs = get_favorites(fake_get, fake_names)
    assert favs.count("mychain") == 1


def test_remove_favorite_success():
    fake_get, fake_add, fake_names, store = _make_fns({"mychain": {"A": "1"}})
    add_favorite("mychain", "pass", fake_get, fake_names, fake_add)
    remove_favorite("mychain", "pass", fake_get, fake_names, fake_add)
    assert "mychain" not in get_favorites(fake_get, fake_names)


def test_remove_favorite_not_favorited_raises():
    fake_get, fake_add, fake_names, store = _make_fns({"mychain": {"A": "1"}})
    with pytest.raises(FavoriteError):
        remove_favorite("mychain", "pass", fake_get, fake_names, fake_add)


def test_is_favorite_true_and_false():
    fake_get, fake_add, fake_names, store = _make_fns({"alpha": {"X": "1"}})
    assert not is_favorite("alpha", fake_get, fake_names)
    add_favorite("alpha", "pass", fake_get, fake_names, fake_add)
    assert is_favorite("alpha", fake_get, fake_names)


def test_get_favorites_empty():
    fake_get, fake_add, fake_names, store = _make_fns()
    assert get_favorites(fake_get, fake_names) == []
