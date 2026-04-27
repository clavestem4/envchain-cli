"""Tests for envchain.ownership."""

import pytest
from unittest.mock import patch, MagicMock
from envchain.ownership import (
    OwnershipError,
    set_owner,
    get_owner,
    clear_owner,
    list_by_owner,
    OWNERSHIP_KEY,
)

PASSWORD = "testpass"


@pytest.fixture
def mock_chain_fns():
    store = {}

    def fake_get(name, pw):
        if name not in store:
            raise KeyError(name)
        return dict(store[name])

    def fake_add(name, data, pw, overwrite=False):
        store[name] = dict(data)

    def fake_names(pw):
        return list(store.keys())

    with patch("envchain.ownership.get_chain", side_effect=fake_get), \
         patch("envchain.ownership.add_chain", side_effect=fake_add), \
         patch("envchain.ownership.get_chain_names", side_effect=fake_names):
        store["mychain"] = {"KEY": "val"}
        store["otherchain"] = {"FOO": "bar", OWNERSHIP_KEY: "alice"}
        yield store


def test_set_owner_success(mock_chain_fns):
    set_owner("mychain", "alice", PASSWORD)
    assert mock_chain_fns["mychain"][OWNERSHIP_KEY] == "alice"


def test_set_owner_missing_chain(mock_chain_fns):
    with pytest.raises(OwnershipError, match="does not exist"):
        set_owner("ghost", "alice", PASSWORD)


def test_set_owner_empty_owner(mock_chain_fns):
    with pytest.raises(OwnershipError, match="must not be empty"):
        set_owner("mychain", "  ", PASSWORD)


def test_get_owner_set(mock_chain_fns):
    mock_chain_fns["mychain"][OWNERSHIP_KEY] = "bob"
    assert get_owner("mychain", PASSWORD) == "bob"


def test_get_owner_unset(mock_chain_fns):
    assert get_owner("mychain", PASSWORD) is None


def test_get_owner_missing_chain(mock_chain_fns):
    with pytest.raises(OwnershipError, match="does not exist"):
        get_owner("ghost", PASSWORD)


def test_clear_owner(mock_chain_fns):
    mock_chain_fns["mychain"][OWNERSHIP_KEY] = "carol"
    clear_owner("mychain", PASSWORD)
    assert OWNERSHIP_KEY not in mock_chain_fns["mychain"]


def test_clear_owner_not_set(mock_chain_fns):
    # Should not raise even if key is absent
    clear_owner("mychain", PASSWORD)
    assert OWNERSHIP_KEY not in mock_chain_fns["mychain"]


def test_list_by_owner(mock_chain_fns):
    mock_chain_fns["mychain"][OWNERSHIP_KEY] = "alice"
    results = list_by_owner("alice", PASSWORD)
    assert "otherchain" in results
    assert "mychain" in results


def test_list_by_owner_no_match(mock_chain_fns):
    results = list_by_owner("nobody", PASSWORD)
    assert results == []
