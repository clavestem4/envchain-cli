"""Tests for envchain.criticality module."""

import pytest
from unittest.mock import patch, MagicMock
from envchain.criticality import (
    set_criticality,
    get_criticality,
    clear_criticality,
    list_by_criticality,
    CriticalityError,
)

PASSWORD = "testpass"


@pytest.fixture
def mock_chain_fns():
    chains = {}

    def fake_get(name, pw):
        if name not in chains:
            raise KeyError(name)
        return dict(chains[name])

    def fake_add(name, data, pw):
        chains[name] = dict(data)

    def fake_update(name, data, pw):
        chains[name] = dict(data)

    def fake_names(pw):
        return list(chains.keys())

    with patch("envchain.criticality.get_chain", side_effect=fake_get), \
         patch("envchain.criticality.update_chain", side_effect=fake_update), \
         patch("envchain.criticality.get_chain_names", side_effect=fake_names):
        chains["mychain"] = {"KEY": "value"}
        chains["otherchain"] = {"FOO": "bar"}
        yield chains


def test_set_and_get_criticality(mock_chain_fns):
    set_criticality("mychain", "high", PASSWORD)
    result = get_criticality("mychain", PASSWORD)
    assert result == "high"


def test_set_criticality_invalid_level(mock_chain_fns):
    with pytest.raises(CriticalityError, match="Invalid criticality level"):
        set_criticality("mychain", "extreme", PASSWORD)


def test_get_criticality_unset(mock_chain_fns):
    result = get_criticality("mychain", PASSWORD)
    assert result is None


def test_clear_criticality(mock_chain_fns):
    set_criticality("mychain", "critical", PASSWORD)
    clear_criticality("mychain", PASSWORD)
    assert get_criticality("mychain", PASSWORD) is None


def test_clear_criticality_not_set(mock_chain_fns):
    # Should not raise even if not set
    clear_criticality("mychain", PASSWORD)
    assert get_criticality("mychain", PASSWORD) is None


def test_list_by_criticality(mock_chain_fns):
    set_criticality("mychain", "high", PASSWORD)
    set_criticality("otherchain", "low", PASSWORD)
    results = list_by_criticality("high", PASSWORD)
    assert "mychain" in results
    assert "otherchain" not in results


def test_list_by_criticality_invalid_level(mock_chain_fns):
    with pytest.raises(CriticalityError, match="Invalid criticality level"):
        list_by_criticality("unknown", PASSWORD)


def test_set_criticality_missing_chain(mock_chain_fns):
    with pytest.raises(KeyError):
        set_criticality("nonexistent", "medium", PASSWORD)
