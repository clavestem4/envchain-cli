"""Tests for envchain.expire module."""

import pytest
from datetime import datetime, timezone, timedelta
from unittest.mock import patch, MagicMock

from envchain.expire import (
    set_expiry, get_expiry, clear_expiry, is_expired, list_expired, EXPIRY_KEY
)

FUTURE = datetime.now(timezone.utc) + timedelta(days=1)
PAST = datetime.now(timezone.utc) - timedelta(days=1)


@pytest.fixture
def mock_chain_fns():
    store = {}

    def fake_get(name, pw):
        if name not in store:
            raise KeyError(name)
        return dict(store[name])

    def fake_add(name, pw, data, overwrite=False):
        store[name] = dict(data)

    def fake_names():
        return list(store.keys())

    with patch("envchain.expire.get_chain", side_effect=fake_get), \
         patch("envchain.expire.add_chain", side_effect=fake_add), \
         patch("envchain.expire.get_chain_names", side_effect=fake_names):
        store["mychain"] = {"FOO": "bar"}
        yield store


def test_set_and_get_expiry(mock_chain_fns):
    set_expiry("mychain", "pass", FUTURE)
    result = get_expiry("mychain", "pass")
    assert result is not None
    assert abs((result - FUTURE).total_seconds()) < 1


def test_get_expiry_none_when_not_set(mock_chain_fns):
    assert get_expiry("mychain", "pass") is None


def test_clear_expiry(mock_chain_fns):
    set_expiry("mychain", "pass", FUTURE)
    clear_expiry("mychain", "pass")
    assert get_expiry("mychain", "pass") is None
    assert EXPIRY_KEY not in mock_chain_fns["mychain"]


def test_is_expired_false_for_future(mock_chain_fns):
    set_expiry("mychain", "pass", FUTURE)
    assert is_expired("mychain", "pass") is False


def test_is_expired_true_for_past(mock_chain_fns):
    set_expiry("mychain", "pass", PAST)
    assert is_expired("mychain", "pass") is True


def test_is_expired_false_when_no_expiry(mock_chain_fns):
    assert is_expired("mychain", "pass") is False


def test_list_expired(mock_chain_fns):
    mock_chain_fns["old"] = {"X": "1"}
    mock_chain_fns["fresh"] = {"Y": "2"}
    set_expiry("old", "pass", PAST)
    set_expiry("fresh", "pass", FUTURE)
    expired = list_expired("pass")
    assert "old" in expired
    assert "fresh" not in expired
    assert "mychain" not in expired
