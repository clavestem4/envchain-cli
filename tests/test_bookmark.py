"""Tests for envchain.bookmark."""

import pytest
from envchain.bookmark import add_bookmark, remove_bookmark, get_bookmarks, is_bookmarked, BookmarkError

BOOKMARK_KEY = "__bookmarks__"


@pytest.fixture
def mock_chain_fns():
    store = {}

    def fake_get(name):
        if name not in store:
            raise KeyError(name)
        return store[name]

    def fake_add(name, data, overwrite=False):
        store[name] = data

    return fake_get, fake_add, store


def test_add_bookmark_success(mock_chain_fns):
    get_fn, add_fn, store = mock_chain_fns
    store["mychain"] = {"FOO": "bar"}
    add_bookmark("mychain", get_fn=get_fn, add_fn=add_fn)
    assert "mychain" in store[BOOKMARK_KEY]["chains"]


def test_add_bookmark_missing_chain(mock_chain_fns):
    get_fn, add_fn, _ = mock_chain_fns
    with pytest.raises(BookmarkError, match="does not exist"):
        add_bookmark("ghost", get_fn=get_fn, add_fn=add_fn)


def test_add_bookmark_duplicate(mock_chain_fns):
    get_fn, add_fn, store = mock_chain_fns
    store["mychain"] = {"X": "1"}
    add_bookmark("mychain", get_fn=get_fn, add_fn=add_fn)
    add_bookmark("mychain", get_fn=get_fn, add_fn=add_fn)
    assert store[BOOKMARK_KEY]["chains"].count("mychain") == 1


def test_remove_bookmark_success(mock_chain_fns):
    get_fn, add_fn, store = mock_chain_fns
    store["mychain"] = {"X": "1"}
    store[BOOKMARK_KEY] = {"chains": ["mychain"]}
    remove_bookmark("mychain", get_fn=get_fn, add_fn=add_fn)
    assert "mychain" not in store[BOOKMARK_KEY]["chains"]


def test_remove_bookmark_not_bookmarked(mock_chain_fns):
    get_fn, add_fn, _ = mock_chain_fns
    with pytest.raises(BookmarkError, match="not bookmarked"):
        remove_bookmark("nope", get_fn=get_fn, add_fn=add_fn)


def test_is_bookmarked(mock_chain_fns):
    get_fn, add_fn, store = mock_chain_fns
    store[BOOKMARK_KEY] = {"chains": ["alpha"]}
    assert is_bookmarked("alpha", get_fn=get_fn, add_fn=add_fn) is True
    assert is_bookmarked("beta", get_fn=get_fn, add_fn=add_fn) is False


def test_get_bookmarks_empty(mock_chain_fns):
    get_fn, add_fn, _ = mock_chain_fns
    result = get_bookmarks(get_fn=get_fn, add_fn=add_fn)
    assert result == []
