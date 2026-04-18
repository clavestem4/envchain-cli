"""Tests for envchain.pin module."""
import pytest
from unittest.mock import MagicMock
from envchain.pin import pin_chain, unpin_chain, get_pinned, is_pinned, _PINS_CHAIN


def _make_fns(store=None):
    if store is None:
        store = {}

    def fake_get(name):
        if name not in store:
            raise KeyError(name)
        return store[name]

    def fake_add(name, data, overwrite=False):
        store[name] = data

    return fake_get, fake_add, store


def test_pin_chain_adds_to_pins():
    get_fn, add_fn, store = _make_fns({"mychain": {"A": "1"}})
    pin_chain("mychain", get_chain_fn=get_fn, add_chain_fn=add_fn)
    assert "mychain" in store[_PINS_CHAIN]


def test_pin_chain_missing_raises():
    get_fn, add_fn, _ = _make_fns({})
    with pytest.raises(KeyError):
        pin_chain("ghost", get_chain_fn=get_fn, add_chain_fn=add_fn)


def test_pin_internal_chain_raises():
    get_fn, add_fn, _ = _make_fns()
    with pytest.raises(ValueError):
        pin_chain("__pins__", get_chain_fn=get_fn, add_chain_fn=add_fn)


def test_pin_duplicate_is_idempotent():
    get_fn, add_fn, store = _make_fns({"c": {}})
    pin_chain("c", get_chain_fn=get_fn, add_chain_fn=add_fn)
    pin_chain("c", get_chain_fn=get_fn, add_chain_fn=add_fn)
    assert list(store[_PINS_CHAIN].keys()).count("c") == 1


def test_unpin_chain():
    store = {"c": {}, _PINS_CHAIN: {"c": "1"}}
    get_fn, add_fn, store = _make_fns(store)
    unpin_chain("c", get_chain_fn=get_fn, add_chain_fn=add_fn)
    assert "c" not in store.get(_PINS_CHAIN, {})


def test_unpin_not_pinned_raises():
    get_fn, add_fn, _ = _make_fns({})
    with pytest.raises(KeyError):
        unpin_chain("nope", get_chain_fn=get_fn, add_chain_fn=add_fn)


def test_get_pinned_empty():
    get_fn, add_fn, _ = _make_fns({})
    assert get_pinned(get_chain_fn=get_fn) == []


def test_is_pinned_true_and_false():
    store = {"a": {}, _PINS_CHAIN: {"a": "1"}}
    get_fn, add_fn, _ = _make_fns(store)
    assert is_pinned("a", get_chain_fn=get_fn) is True
    assert is_pinned("b", get_chain_fn=get_fn) is False
