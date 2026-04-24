"""Tests for envchain.permission module."""

import pytest
from unittest.mock import patch, MagicMock
from envchain.permission import (
    PermissionError,
    set_permission,
    get_permission,
    revoke_permission,
    has_permission,
    list_permissions,
    find_chains_for_user,
)


@pytest.fixture
def mock_chain_fns():
    store = {}

    def fake_get(name):
        if name not in store:
            raise KeyError(name)
        return dict(store[name])

    def fake_add(name, data, overwrite=False):
        store[name] = dict(data)

    def fake_names():
        return list(store.keys())

    store["mychain"] = {"FOO": "bar"}

    with patch("envchain.permission.get_chain", side_effect=fake_get), \
         patch("envchain.permission.add_chain", side_effect=fake_add), \
         patch("envchain.permission.get_chain_names", side_effect=fake_names):
        yield store


def test_set_and_get_permission(mock_chain_fns):
    set_permission("mychain", "alice", ["read", "write"])
    perms = get_permission("mychain", "alice")
    assert "read" in perms
    assert "write" in perms


def test_set_permission_invalid(mock_chain_fns):
    with pytest.raises(PermissionError, match="Invalid permissions"):
        set_permission("mychain", "alice", ["read", "delete"])


def test_get_permission_unset(mock_chain_fns):
    perms = get_permission("mychain", "bob")
    assert perms == []


def test_revoke_permission(mock_chain_fns):
    set_permission("mychain", "alice", ["exec"])
    revoke_permission("mychain", "alice")
    assert get_permission("mychain", "alice") == []


def test_revoke_permission_not_set(mock_chain_fns):
    with pytest.raises(PermissionError, match="no permissions"):
        revoke_permission("mychain", "nobody")


def test_has_permission_true(mock_chain_fns):
    set_permission("mychain", "alice", ["read"])
    assert has_permission("mychain", "alice", "read") is True


def test_has_permission_false(mock_chain_fns):
    set_permission("mychain", "alice", ["read"])
    assert has_permission("mychain", "alice", "write") is False


def test_list_permissions(mock_chain_fns):
    set_permission("mychain", "alice", ["read"])
    set_permission("mychain", "bob", ["write", "exec"])
    result = list_permissions("mychain")
    assert "alice" in result
    assert "bob" in result
    assert result["alice"] == ["read"]


def test_find_chains_for_user(mock_chain_fns):
    mock_chain_fns["other"] = {"X": "1"}
    set_permission("mychain", "alice", ["read"])
    found = find_chains_for_user("alice")
    assert "mychain" in found
    assert "other" not in found


def test_find_chains_for_user_with_perm_filter(mock_chain_fns):
    set_permission("mychain", "alice", ["read"])
    assert find_chains_for_user("alice", "read") == ["mychain"]
    assert find_chains_for_user("alice", "exec") == []
