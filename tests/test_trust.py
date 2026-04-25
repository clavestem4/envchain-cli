"""Tests for envchain.trust module."""

import pytest
from unittest.mock import patch, MagicMock
from envchain.trust import (
    set_trust,
    get_trust,
    clear_trust,
    list_by_trust,
    TrustError,
    TRUST_KEY,
)


@pytest.fixture
def mock_chain_fns():
    store = {}

    def fake_get(name, password):
        if name not in store:
            raise KeyError(f"Chain '{name}' not found")
        return dict(store[name])

    def fake_add(name, data, password):
        store[name] = dict(data)

    def fake_names(password):
        return list(store.keys())

    with patch("envchain.trust.get_chain", side_effect=fake_get), \
         patch("envchain.trust.add_chain", side_effect=fake_add), \
         patch("envchain.trust.get_chain_names", side_effect=fake_names):
        store["mychain"] = {"KEY": "value"}
        store["otherchain"] = {"FOO": "bar", TRUST_KEY: "high"}
        yield store


def test_set_and_get_trust(mock_chain_fns):
    set_trust("mychain", "medium", "pass")
    result = get_trust("mychain", "pass")
    assert result == "medium"


def test_set_trust_invalid_level(mock_chain_fns):
    with pytest.raises(TrustError, match="Invalid trust level"):
        set_trust("mychain", "superduper", "pass")


def test_get_trust_unset(mock_chain_fns):
    result = get_trust("mychain", "pass")
    assert result is None


def test_get_trust_existing(mock_chain_fns):
    result = get_trust("otherchain", "pass")
    assert result == "high"


def test_clear_trust(mock_chain_fns):
    set_trust("mychain", "low", "pass")
    clear_trust("mychain", "pass")
    assert get_trust("mychain", "pass") is None


def test_clear_trust_not_set(mock_chain_fns):
    # Should not raise even if not set
    clear_trust("mychain", "pass")
    assert get_trust("mychain", "pass") is None


def test_list_by_trust(mock_chain_fns):
    set_trust("mychain", "verified", "pass")
    results = list_by_trust("verified", "pass")
    assert "mychain" in results
    assert "otherchain" not in results


def test_list_by_trust_multiple(mock_chain_fns):
    set_trust("mychain", "high", "pass")
    results = list_by_trust("high", "pass")
    assert "mychain" in results
    assert "otherchain" in results


def test_list_by_trust_invalid_level(mock_chain_fns):
    with pytest.raises(TrustError, match="Invalid trust level"):
        list_by_trust("bogus", "pass")


def test_set_trust_missing_chain(mock_chain_fns):
    with pytest.raises(KeyError):
        set_trust("nonexistent", "low", "pass")
