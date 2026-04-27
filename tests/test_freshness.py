import pytest
from datetime import datetime, timezone, timedelta
from unittest.mock import MagicMock
from envchain.freshness import (
    set_freshness,
    get_freshness,
    clear_freshness,
    is_stale,
    list_stale,
    FreshnessError,
    _parse_max_age,
)


@pytest.fixture
def mock_chain_fns():
    store = {}

    def fake_get(name):
        return dict(store[name]) if name in store else None

    def fake_add(name, data, overwrite=False):
        store[name] = dict(data)

    def fake_names():
        return list(store.keys())

    return fake_get, fake_add, fake_names, store


def test_parse_max_age_days(mock_chain_fns):
    td = _parse_max_age("7 days")
    assert td == timedelta(days=7)


def test_parse_max_age_hours(mock_chain_fns):
    td = _parse_max_age("12 hours")
    assert td == timedelta(hours=12)


def test_parse_max_age_invalid_format():
    with pytest.raises(FreshnessError, match="Invalid max_age format"):
        _parse_max_age("badvalue")


def test_parse_max_age_invalid_unit():
    with pytest.raises(FreshnessError, match="Invalid unit"):
        _parse_max_age("5 fortnights")


def test_set_and_get_freshness(mock_chain_fns):
    fake_get, fake_add, _, store = mock_chain_fns
    store["mychain"] = {"KEY": "val"}
    set_freshness("mychain", "7 days", fake_get, fake_add)
    meta = get_freshness("mychain", fake_get)
    assert meta is not None
    assert meta["max_age"] == "7 days"
    assert "updated_at" in meta


def test_set_freshness_missing_chain(mock_chain_fns):
    fake_get, fake_add, _, _ = mock_chain_fns
    with pytest.raises(FreshnessError, match="not found"):
        set_freshness("ghost", "1 days", fake_get, fake_add)


def test_clear_freshness(mock_chain_fns):
    fake_get, fake_add, _, store = mock_chain_fns
    store["mychain"] = {"KEY": "val", "__freshness__": {"max_age": "1 days"}}
    clear_freshness("mychain", fake_get, fake_add)
    meta = get_freshness("mychain", fake_get)
    assert meta is None


def test_is_stale_when_expired(mock_chain_fns):
    fake_get, fake_add, _, store = mock_chain_fns
    old_time = (datetime.now(timezone.utc) - timedelta(days=10)).isoformat()
    store["mychain"] = {"__freshness__": {"max_age": "7 days", "updated_at": old_time}}
    assert is_stale("mychain", fake_get) is True


def test_is_stale_when_fresh(mock_chain_fns):
    fake_get, fake_add, _, store = mock_chain_fns
    recent = datetime.now(timezone.utc).isoformat()
    store["mychain"] = {"__freshness__": {"max_age": "7 days", "updated_at": recent}}
    assert is_stale("mychain", fake_get) is False


def test_is_stale_no_policy(mock_chain_fns):
    fake_get, _, _, store = mock_chain_fns
    store["mychain"] = {"KEY": "val"}
    assert is_stale("mychain", fake_get) is False


def test_list_stale(mock_chain_fns):
    fake_get, _, fake_names, store = mock_chain_fns
    old = (datetime.now(timezone.utc) - timedelta(days=30)).isoformat()
    recent = datetime.now(timezone.utc).isoformat()
    store["old_chain"] = {"__freshness__": {"max_age": "7 days", "updated_at": old}}
    store["new_chain"] = {"__freshness__": {"max_age": "7 days", "updated_at": recent}}
    stale = list_stale(fake_names, fake_get)
    assert "old_chain" in stale
    assert "new_chain" not in stale
