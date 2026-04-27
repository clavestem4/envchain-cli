"""Tests for envchain.impact module."""

import pytest
from unittest.mock import patch
from envchain.impact import (
    ImpactError,
    set_impact,
    get_impact,
    clear_impact,
    list_by_impact,
)


@pytest.fixture
def mock_chain_fns():
    store = {}

    def fake_get(name, password):
        if name not in store:
            raise KeyError(name)
        return dict(store[name])

    def fake_add(name, data, password):
        store[name] = dict(data)

    def fake_update(name, data, password):
        store[name] = dict(data)

    def fake_names(password):
        return list(store.keys())

    with patch("envchain.impact.get_chain", side_effect=fake_get), \
         patch("envchain.impact.update_chain", side_effect=fake_update), \
         patch("envchain.impact.get_chain_names", side_effect=fake_names):
        yield store


def fake_get(store):
    def _get(name, password):
        if name not in store:
            raise KeyError(name)
        return dict(store[name])
    return _get


def fake_add(store):
    def _add(name, data, password):
        store[name] = dict(data)
    return _add


def test_set_and_get_impact(mock_chain_fns):
    mock_chain_fns["mychain"] = {"KEY": "val"}
    set_impact("mychain", "high", "pass")
    level = get_impact("mychain", "pass")
    assert level == "high"


def test_set_impact_invalid_level(mock_chain_fns):
    mock_chain_fns["mychain"] = {"KEY": "val"}
    with pytest.raises(ImpactError, match="Invalid impact level"):
        set_impact("mychain", "extreme", "pass")


def test_set_impact_missing_chain(mock_chain_fns):
    with pytest.raises(KeyError):
        set_impact("ghost", "low", "pass")


def test_get_impact_unset(mock_chain_fns):
    mock_chain_fns["mychain"] = {"KEY": "val"}
    result = get_impact("mychain", "pass")
    assert result is None


def test_clear_impact(mock_chain_fns):
    mock_chain_fns["mychain"] = {"KEY": "val", "__impact__": "medium"}
    clear_impact("mychain", "pass")
    assert get_impact("mychain", "pass") is None


def test_list_by_impact(mock_chain_fns):
    mock_chain_fns["chain_a"] = {"__impact__": "critical"}
    mock_chain_fns["chain_b"] = {"__impact__": "low"}
    mock_chain_fns["chain_c"] = {"__impact__": "critical"}
    results = list_by_impact("critical", "pass")
    assert set(results) == {"chain_a", "chain_c"}


def test_list_by_impact_none_match(mock_chain_fns):
    mock_chain_fns["chain_a"] = {"__impact__": "low"}
    results = list_by_impact("high", "pass")
    assert results == []


def test_list_by_impact_invalid_level(mock_chain_fns):
    with pytest.raises(ImpactError, match="Invalid impact level"):
        list_by_impact("unknown", "pass")


def test_set_impact_case_insensitive(mock_chain_fns):
    mock_chain_fns["mychain"] = {"KEY": "val"}
    set_impact("mychain", "HIGH", "pass")
    assert get_impact("mychain", "pass") == "high"
