"""Tests for envchain.region module."""

import pytest
from unittest.mock import patch
from envchain.region import (
    set_region,
    get_region,
    clear_region,
    list_by_region,
    RegionError,
)

PASSWORD = "testpass"


@pytest.fixture
def mock_chain_fns():
    store = {}

    def fake_get(name, pw):
        return dict(store[name]) if name in store else None

    def fake_add(name, data, pw):
        store[name] = dict(data)

    def fake_names(pw):
        return list(store.keys())

    with patch("envchain.region.get_chain", side_effect=fake_get), \
         patch("envchain.region.add_chain", side_effect=fake_add), \
         patch("envchain.region.get_chain_names", side_effect=fake_names):
        yield store


def test_set_and_get_region(mock_chain_fns):
    mock_chain_fns["myapp"] = {"DB_URL": "postgres://localhost"}
    set_region("myapp", "prod", PASSWORD)
    assert get_region("myapp", PASSWORD) == "prod"


def test_set_region_invalid(mock_chain_fns):
    mock_chain_fns["myapp"] = {}
    with pytest.raises(RegionError, match="Invalid region"):
        set_region("myapp", "production", PASSWORD)


def test_set_region_missing_chain(mock_chain_fns):
    with pytest.raises(RegionError, match="not found"):
        set_region("ghost", "dev", PASSWORD)


def test_get_region_unset(mock_chain_fns):
    mock_chain_fns["myapp"] = {"KEY": "val"}
    assert get_region("myapp", PASSWORD) is None


def test_get_region_missing_chain(mock_chain_fns):
    with pytest.raises(RegionError, match="not found"):
        get_region("ghost", PASSWORD)


def test_clear_region(mock_chain_fns):
    mock_chain_fns["myapp"] = {"__region__": "staging", "KEY": "val"}
    clear_region("myapp", PASSWORD)
    assert get_region("myapp", PASSWORD) is None


def test_clear_region_missing_chain(mock_chain_fns):
    with pytest.raises(RegionError, match="not found"):
        clear_region("ghost", PASSWORD)


def test_list_by_region(mock_chain_fns):
    mock_chain_fns["app1"] = {"__region__": "dev"}
    mock_chain_fns["app2"] = {"__region__": "prod"}
    mock_chain_fns["app3"] = {"__region__": "dev"}
    result = list_by_region("dev", PASSWORD)
    assert sorted(result) == ["app1", "app3"]


def test_list_by_region_empty(mock_chain_fns):
    mock_chain_fns["app1"] = {"__region__": "staging"}
    result = list_by_region("prod", PASSWORD)
    assert result == []


def test_list_by_region_invalid(mock_chain_fns):
    with pytest.raises(RegionError, match="Invalid region"):
        list_by_region("unknown", PASSWORD)
