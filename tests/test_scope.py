"""Tests for envchain.scope module."""

import pytest
from unittest.mock import patch, MagicMock
from envchain.scope import (
    set_scope,
    get_scope,
    clear_scope,
    list_by_scope,
    ScopeError,
    VALID_SCOPES,
)


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

    with patch("envchain.scope.get_chain", side_effect=fake_get), \
         patch("envchain.scope.add_chain", side_effect=fake_add), \
         patch("envchain.scope.get_chain_names", side_effect=fake_names):
        yield store


def test_set_and_get_scope(mock_chain_fns):
    mock_chain_fns["mychain"] = {"API_KEY": "abc"}
    set_scope("mychain", "dev", "pass")
    assert get_scope("mychain", "pass") == "dev"


def test_set_scope_invalid(mock_chain_fns):
    mock_chain_fns["mychain"] = {"API_KEY": "abc"}
    with pytest.raises(ScopeError, match="Invalid scope"):
        set_scope("mychain", "unknown", "pass")


def test_set_scope_missing_chain(mock_chain_fns):
    with pytest.raises(ScopeError, match="does not exist"):
        set_scope("ghost", "prod", "pass")


def test_get_scope_unset(mock_chain_fns):
    mock_chain_fns["mychain"] = {"FOO": "bar"}
    assert get_scope("mychain", "pass") is None


def test_get_scope_missing_chain(mock_chain_fns):
    with pytest.raises(ScopeError, match="does not exist"):
        get_scope("ghost", "pass")


def test_clear_scope(mock_chain_fns):
    mock_chain_fns["mychain"] = {"FOO": "bar", "__scope__": "staging"}
    clear_scope("mychain", "pass")
    assert get_scope("mychain", "pass") is None


def test_clear_scope_missing_chain(mock_chain_fns):
    with pytest.raises(ScopeError, match="does not exist"):
        clear_scope("ghost", "pass")


def test_list_by_scope(mock_chain_fns):
    mock_chain_fns["alpha"] = {"X": "1", "__scope__": "prod"}
    mock_chain_fns["beta"] = {"Y": "2", "__scope__": "dev"}
    mock_chain_fns["gamma"] = {"Z": "3", "__scope__": "prod"}
    result = list_by_scope("prod", "pass")
    assert sorted(result) == ["alpha", "gamma"]


def test_list_by_scope_no_match(mock_chain_fns):
    mock_chain_fns["alpha"] = {"X": "1", "__scope__": "dev"}
    result = list_by_scope("ci", "pass")
    assert result == []


def test_list_by_scope_invalid(mock_chain_fns):
    with pytest.raises(ScopeError, match="Invalid scope"):
        list_by_scope("nope", "pass")


def test_all_valid_scopes_accepted(mock_chain_fns):
    mock_chain_fns["chain"] = {"K": "v"}
    for scope in VALID_SCOPES:
        set_scope("chain", scope, "pass")
        assert get_scope("chain", "pass") == scope
