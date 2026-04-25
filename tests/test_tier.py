"""Tests for envchain.tier module."""

import pytest
from unittest.mock import patch
from envchain.tier import (
    set_tier,
    get_tier,
    clear_tier,
    list_by_tier,
    TierError,
    VALID_TIERS,
)

PASSWORD = "test-password"


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

    with patch("envchain.tier.get_chain", side_effect=fake_get), \
         patch("envchain.tier.add_chain", side_effect=fake_add), \
         patch("envchain.tier.get_chain_names", side_effect=fake_names):
        store["mychain"] = {"KEY": "value"}
        store["otherchain"] = {"FOO": "bar", "__tier__": "pro"}
        yield store


def test_set_and_get_tier(mock_chain_fns):
    set_tier("mychain", "pro", PASSWORD)
    result = get_tier("mychain", PASSWORD)
    assert result == "pro"


def test_set_tier_invalid(mock_chain_fns):
    with pytest.raises(TierError, match="Invalid tier"):
        set_tier("mychain", "platinum", PASSWORD)


def test_set_tier_missing_chain(mock_chain_fns):
    with pytest.raises(TierError, match="not found"):
        set_tier("ghost", "free", PASSWORD)


def test_get_tier_unset(mock_chain_fns):
    result = get_tier("mychain", PASSWORD)
    assert result is None


def test_get_tier_missing_chain(mock_chain_fns):
    with pytest.raises(TierError, match="not found"):
        get_tier("ghost", PASSWORD)


def test_clear_tier(mock_chain_fns):
    set_tier("mychain", "enterprise", PASSWORD)
    clear_tier("mychain", PASSWORD)
    assert get_tier("mychain", PASSWORD) is None


def test_clear_tier_no_tier_set(mock_chain_fns):
    # Should not raise even if tier was never set
    clear_tier("mychain", PASSWORD)
    assert get_tier("mychain", PASSWORD) is None


def test_list_by_tier(mock_chain_fns):
    set_tier("mychain", "pro", PASSWORD)
    results = list_by_tier("pro", PASSWORD)
    assert "mychain" in results
    assert "otherchain" in results


def test_list_by_tier_no_match(mock_chain_fns):
    results = list_by_tier("legacy", PASSWORD)
    assert results == []


def test_list_by_tier_invalid(mock_chain_fns):
    with pytest.raises(TierError, match="Invalid tier"):
        list_by_tier("unknown", PASSWORD)


def test_valid_tiers_set():
    assert "free" in VALID_TIERS
    assert "pro" in VALID_TIERS
    assert "enterprise" in VALID_TIERS
