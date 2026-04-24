"""Tests for envchain.retention module."""

from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock
import pytest

from envchain.retention import (
    RetentionError,
    set_retention,
    get_retention,
    clear_retention,
    is_retention_expired,
    list_expired_retention,
)


@pytest.fixture
def mock_chain_fns():
    store = {}

    def fake_get(name, password):
        if name not in store:
            raise KeyError(name)
        return dict(store[name])

    def fake_add(name, data, password, overwrite=False):
        store[name] = dict(data)

    def fake_names(password):
        return list(store.keys())

    with patch("envchain.retention.get_chain", side_effect=fake_get), \
         patch("envchain.retention.add_chain", side_effect=fake_add), \
         patch("envchain.retention.get_chain_names", side_effect=fake_names):
        store["mychain"] = {"KEY": "val"}
        yield store


def test_set_and_get_retention(mock_chain_fns):
    set_retention("mychain", 30, "pass")
    days = get_retention("mychain", "pass")
    assert days == 30


def test_set_retention_invalid_days(mock_chain_fns):
    with pytest.raises(RetentionError):
        set_retention("mychain", -5, "pass")


def test_set_retention_zero_days(mock_chain_fns):
    with pytest.raises(RetentionError):
        set_retention("mychain", 0, "pass")


def test_get_retention_unset(mock_chain_fns):
    result = get_retention("mychain", "pass")
    assert result is None


def test_clear_retention(mock_chain_fns):
    set_retention("mychain", 10, "pass")
    clear_retention("mychain", "pass")
    assert get_retention("mychain", "pass") is None


def test_is_retention_expired_not_expired(mock_chain_fns):
    set_retention("mychain", 30, "pass")
    assert is_retention_expired("mychain", "pass") is False


def test_is_retention_expired_past_date(mock_chain_fns):
    set_retention("mychain", 1, "pass")
    old_date = (datetime.utcnow() - timedelta(days=5)).isoformat()
    mock_chain_fns["mychain"]["__meta__"]["retention_set_at"] = old_date
    assert is_retention_expired("mychain", "pass") is True


def test_is_retention_expired_no_policy(mock_chain_fns):
    assert is_retention_expired("mychain", "pass") is False


def test_list_expired_retention(mock_chain_fns):
    mock_chain_fns["other"] = {"X": "1"}
    set_retention("mychain", 1, "pass")
    old_date = (datetime.utcnow() - timedelta(days=10)).isoformat()
    mock_chain_fns["mychain"]["__meta__"]["retention_set_at"] = old_date
    expired = list_expired_retention("pass")
    assert "mychain" in expired
    assert "other" not in expired


def test_list_expired_retention_none_expired(mock_chain_fns):
    set_retention("mychain", 90, "pass")
    expired = list_expired_retention("pass")
    assert expired == []
