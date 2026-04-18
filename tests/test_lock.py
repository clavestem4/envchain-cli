"""Tests for envchain.lock."""

import pytest
from unittest.mock import patch, MagicMock
from envchain import lock as lock_mod


@pytest.fixture
def mock_chain_fns():
    store = {}

    def fake_get(name, password):
        if name not in store:
            raise KeyError(f"Chain '{name}' not found")
        return dict(store[name])

    def fake_add(name, data, password, overwrite=False):
        store[name] = dict(data)

    def fake_names():
        return list(store.keys())

    with patch.object(lock_mod, "get_chain", side_effect=fake_get), \
         patch.object(lock_mod, "add_chain", side_effect=fake_add), \
         patch.object(lock_mod, "get_chain_names", side_effect=fake_names):
        store["mychain"] = {"KEY": "value"}
        yield store


def test_lock_chain(mock_chain_fns):
    lock_mod.lock_chain("mychain", "pass")
    assert mock_chain_fns["mychain"]["__locked__"] == "true"


def test_lock_chain_already_locked(mock_chain_fns):
    lock_mod.lock_chain("mychain", "pass")
    with pytest.raises(ValueError, match="already locked"):
        lock_mod.lock_chain("mychain", "pass")


def test_unlock_chain(mock_chain_fns):
    lock_mod.lock_chain("mychain", "pass")
    lock_mod.unlock_chain("mychain", "pass")
    assert "__locked__" not in mock_chain_fns["mychain"]


def test_unlock_chain_not_locked(mock_chain_fns):
    with pytest.raises(ValueError, match="not locked"):
        lock_mod.unlock_chain("mychain", "pass")


def test_is_locked_true(mock_chain_fns):
    lock_mod.lock_chain("mychain", "pass")
    assert lock_mod.is_locked("mychain", "pass") is True


def test_is_locked_false(mock_chain_fns):
    assert lock_mod.is_locked("mychain", "pass") is False


def test_list_locked(mock_chain_fns):
    mock_chain_fns["other"] = {"X": "1"}
    lock_mod.lock_chain("mychain", "pass")
    result = lock_mod.list_locked("pass")
    assert "mychain" in result
    assert "other" not in result
