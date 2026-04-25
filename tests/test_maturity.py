"""Tests for envchain.maturity module."""

import pytest
from unittest.mock import patch, MagicMock
from envchain.maturity import (
    set_maturity,
    get_maturity,
    clear_maturity,
    list_by_maturity,
    MaturityError,
    MATURITY_LEVELS,
)


@pytest.fixture
def mock_chain_fns():
    store = {}

    def fake_get(name, password):
        if name not in store:
            raise KeyError(f"Chain '{name}' not found")
        return dict(store[name])

    def fake_add(name, data, password, overwrite=False):
        store[name] = dict(data)

    def fake_names(password):
        return list(store.keys())

    with patch("envchain.maturity.get_chain", side_effect=fake_get), \
         patch("envchain.maturity.add_chain", side_effect=fake_add), \
         patch("envchain.maturity.get_chain_names", side_effect=fake_names):
        yield store


def test_set_and_get_maturity(mock_chain_fns):
    mock_chain_fns["mychain"] = {"KEY": "val"}
    set_maturity("mychain", "stable", "pass")
    assert get_maturity("mychain", "pass") == "stable"


def test_set_maturity_invalid_level(mock_chain_fns):
    mock_chain_fns["mychain"] = {"KEY": "val"}
    with pytest.raises(MaturityError, match="Invalid maturity level"):
        set_maturity("mychain", "unknown", "pass")


def test_get_maturity_unset(mock_chain_fns):
    mock_chain_fns["mychain"] = {"KEY": "val"}
    assert get_maturity("mychain", "pass") is None


def test_clear_maturity(mock_chain_fns):
    mock_chain_fns["mychain"] = {"KEY": "val", "__maturity__": "experimental"}
    clear_maturity("mychain", "pass")
    assert get_maturity("mychain", "pass") is None


def test_clear_maturity_not_set(mock_chain_fns):
    mock_chain_fns["mychain"] = {"KEY": "val"}
    clear_maturity("mychain", "pass")  # Should not raise
    assert get_maturity("mychain", "pass") is None


def test_list_by_maturity(mock_chain_fns):
    mock_chain_fns["alpha"] = {"X": "1", "__maturity__": "stable"}
    mock_chain_fns["beta"] = {"Y": "2", "__maturity__": "experimental"}
    mock_chain_fns["gamma"] = {"Z": "3", "__maturity__": "stable"}
    result = list_by_maturity("stable", "pass")
    assert sorted(result) == ["alpha", "gamma"]


def test_list_by_maturity_invalid_level(mock_chain_fns):
    with pytest.raises(MaturityError, match="Invalid maturity level"):
        list_by_maturity("bogus", "pass")


def test_list_by_maturity_empty(mock_chain_fns):
    mock_chain_fns["alpha"] = {"X": "1", "__maturity__": "developing"}
    result = list_by_maturity("archived", "pass")
    assert result == []


def test_all_maturity_levels_are_valid(mock_chain_fns):
    mock_chain_fns["chain"] = {"K": "v"}
    for level in MATURITY_LEVELS:
        set_maturity("chain", level, "pass")
        assert get_maturity("chain", "pass") == level
