"""Tests for envchain/archetype.py"""

import pytest
from unittest.mock import patch, MagicMock
from envchain.archetype import (
    set_archetype,
    get_archetype,
    clear_archetype,
    list_by_archetype,
    ArchetypeError,
    ARCHETYPE_KEY,
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

    with patch("envchain.archetype.get_chain", side_effect=fake_get), \
         patch("envchain.archetype.add_chain", side_effect=fake_add), \
         patch("envchain.archetype.get_chain_names", side_effect=fake_names):
        store["mychain"] = {"DB_HOST": "localhost"}
        store["otherchain"] = {"API_KEY": "abc", ARCHETYPE_KEY: "api"}
        store["thirdchain"] = {"TOKEN": "xyz", ARCHETYPE_KEY: "api"}
        yield store


def test_set_archetype_success(mock_chain_fns):
    set_archetype("mychain", "database", "pass")
    assert mock_chain_fns["mychain"][ARCHETYPE_KEY] == "database"


def test_set_archetype_invalid(mock_chain_fns):
    with pytest.raises(ArchetypeError, match="Invalid archetype"):
        set_archetype("mychain", "unknown_type", "pass")


def test_get_archetype_set(mock_chain_fns):
    result = get_archetype("otherchain", "pass")
    assert result == "api"


def test_get_archetype_unset(mock_chain_fns):
    result = get_archetype("mychain", "pass")
    assert result is None


def test_clear_archetype_removes_key(mock_chain_fns):
    clear_archetype("otherchain", "pass")
    assert ARCHETYPE_KEY not in mock_chain_fns["otherchain"]


def test_clear_archetype_no_key_is_noop(mock_chain_fns):
    clear_archetype("mychain", "pass")
    assert ARCHETYPE_KEY not in mock_chain_fns["mychain"]


def test_list_by_archetype_returns_matches(mock_chain_fns):
    results = list_by_archetype("api", "pass")
    assert set(results) == {"otherchain", "thirdchain"}


def test_list_by_archetype_no_match(mock_chain_fns):
    results = list_by_archetype("cache", "pass")
    assert results == []


def test_list_by_archetype_invalid(mock_chain_fns):
    with pytest.raises(ArchetypeError, match="Invalid archetype"):
        list_by_archetype("notreal", "pass")
