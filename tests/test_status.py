"""Tests for envchain.status module."""

import pytest
from unittest.mock import patch
from envchain.status import set_status, get_status, clear_status, list_by_status, StatusError

FAKE_STORE = {}


@pytest.fixture
def mock_chain_fns():
    store = {}

    def fake_get(name, password):
        if name not in store:
            raise KeyError(name)
        return dict(store[name])

    def fake_add(name, data, password, overwrite=False):
        store[name] = dict(data)

    def fake_names(password):
        return list(store.keys())

    with patch("envchain.status.get_chain", side_effect=fake_get), \
         patch("envchain.status.add_chain", side_effect=fake_add), \
         patch("envchain.status.get_chain_names", side_effect=fake_names):
        store["mychain"] = {"VAR": "value"}
        yield store


def test_set_and_get_status(mock_chain_fns):
    set_status("mychain", "inactive", "pass")
    assert get_status("mychain", "pass") == "inactive"


def test_default_status_is_active(mock_chain_fns):
    assert get_status("mychain", "pass") == "active"


def test_set_invalid_status_raises(mock_chain_fns):
    with pytest.raises(StatusError, match="Invalid status"):
        set_status("mychain", "unknown", "pass")


def test_clear_status_resets_to_active(mock_chain_fns):
    set_status("mychain", "archived", "pass")
    clear_status("mychain", "pass")
    assert get_status("mychain", "pass") == "active"


def test_list_by_status(mock_chain_fns):
    mock_chain_fns["other"] = {"X": "1"}
    set_status("mychain", "archived", "pass")
    result = list_by_status("archived", "pass")
    assert "mychain" in result
    assert "other" not in result


def test_list_by_status_invalid_raises(mock_chain_fns):
    with pytest.raises(StatusError):
        list_by_status("pending", "pass")


def test_set_status_missing_chain_raises(mock_chain_fns):
    with pytest.raises(KeyError):
        set_status("ghost", "active", "pass")
