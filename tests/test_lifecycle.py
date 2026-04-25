"""Tests for envchain.lifecycle module."""

import pytest
from unittest.mock import patch
from envchain.lifecycle import (
    set_lifecycle,
    get_lifecycle,
    clear_lifecycle,
    list_by_lifecycle,
    LifecycleError,
    _META_KEY,
)


@pytest.fixture
def mock_chain_fns():
    store = {}

    def fake_get(name, password):
        return dict(store[name]) if name in store else None

    def fake_add(name, data, password, overwrite=False):
        store[name] = dict(data)

    def fake_names(password):
        return list(store.keys())

    with patch("envchain.lifecycle.get_chain", side_effect=fake_get), \
         patch("envchain.lifecycle.add_chain", side_effect=fake_add), \
         patch("envchain.lifecycle.get_chain_names", side_effect=fake_names):
        yield store


def test_set_and_get_lifecycle(mock_chain_fns):
    mock_chain_fns["mychain"] = {"KEY": "value"}
    set_lifecycle("mychain", "active", "pw")
    assert get_lifecycle("mychain", "pw") == "active"


def test_set_lifecycle_invalid_state(mock_chain_fns):
    mock_chain_fns["mychain"] = {"KEY": "value"}
    with pytest.raises(LifecycleError, match="Invalid state"):
        set_lifecycle("mychain", "unknown", "pw")


def test_set_lifecycle_missing_chain(mock_chain_fns):
    with pytest.raises(LifecycleError, match="not found"):
        set_lifecycle("ghost", "active", "pw")


def test_get_lifecycle_unset(mock_chain_fns):
    mock_chain_fns["mychain"] = {"KEY": "value"}
    result = get_lifecycle("mychain", "pw")
    assert result is None


def test_get_lifecycle_missing_chain(mock_chain_fns):
    with pytest.raises(LifecycleError, match="not found"):
        get_lifecycle("ghost", "pw")


def test_clear_lifecycle(mock_chain_fns):
    mock_chain_fns["mychain"] = {"KEY": "value", _META_KEY: "draft"}
    clear_lifecycle("mychain", "pw")
    assert get_lifecycle("mychain", "pw") is None


def test_clear_lifecycle_missing_chain(mock_chain_fns):
    with pytest.raises(LifecycleError, match="not found"):
        clear_lifecycle("ghost", "pw")


def test_list_by_lifecycle(mock_chain_fns):
    mock_chain_fns["a"] = {_META_KEY: "active"}
    mock_chain_fns["b"] = {_META_KEY: "draft"}
    mock_chain_fns["c"] = {_META_KEY: "active"}
    result = list_by_lifecycle("active", "pw")
    assert sorted(result) == ["a", "c"]


def test_list_by_lifecycle_invalid_state(mock_chain_fns):
    with pytest.raises(LifecycleError, match="Invalid state"):
        list_by_lifecycle("unknown", "pw")


def test_list_by_lifecycle_empty(mock_chain_fns):
    mock_chain_fns["a"] = {_META_KEY: "draft"}
    result = list_by_lifecycle("archived", "pw")
    assert result == []
