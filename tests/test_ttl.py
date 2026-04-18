"""Tests for envchain.ttl module."""

import pytest
from datetime import datetime, timedelta, timezone
from unittest.mock import patch, MagicMock
from envchain import ttl as ttl_mod


PASSWORD = "testpass"


@pytest.fixture
def mock_chain_fns():
    store = {}

    def fake_get(name, pw):
        if name not in store:
            raise KeyError(name)
        return dict(store[name])

    def fake_add(name, pw, data, overwrite=False):
        store[name] = dict(data)

    def fake_names(pw):
        return list(store.keys())

    with patch("envchain.ttl.get_chain", side_effect=fake_get), \
         patch("envchain.ttl.add_chain", side_effect=fake_add), \
         patch("envchain.ttl.get_chain_names", side_effect=fake_names):
        store["mychain"] = {"FOO": "bar"}
        yield store


def test_set_and_get_ttl(mock_chain_fns):
    ttl_mod.set_ttl("mychain", PASSWORD, 3600)
    info = ttl_mod.get_ttl("mychain", PASSWORD)
    assert info is not None
    assert info["seconds"] == 3600
    assert not info["expired"]


def test_get_ttl_none_when_not_set(mock_chain_fns):
    result = ttl_mod.get_ttl("mychain", PASSWORD)
    assert result is None


def test_set_ttl_invalid_seconds(mock_chain_fns):
    with pytest.raises(ValueError):
        ttl_mod.set_ttl("mychain", PASSWORD, 0)
    with pytest.raises(ValueError):
        ttl_mod.set_ttl("mychain", PASSWORD, -10)


def test_clear_ttl(mock_chain_fns):
    ttl_mod.set_ttl("mychain", PASSWORD, 60)
    ttl_mod.clear_ttl("mychain", PASSWORD)
    assert ttl_mod.get_ttl("mychain", PASSWORD) is None


def test_is_ttl_expired_false(mock_chain_fns):
    ttl_mod.set_ttl("mychain", PASSWORD, 9999)
    assert ttl_mod.is_ttl_expired("mychain", PASSWORD) is False


def test_is_ttl_expired_true(mock_chain_fns):
    ttl_mod.set_ttl("mychain", PASSWORD, 3600)
    past = datetime.now(timezone.utc) - timedelta(hours=2)
    mock_chain_fns["mychain"]["__ttl_set_at__"] = past.isoformat()
    assert ttl_mod.is_ttl_expired("mychain", PASSWORD) is True


def test_list_expired_ttl(mock_chain_fns):
    mock_chain_fns["other"] = {"A": "1"}
    ttl_mod.set_ttl("mychain", PASSWORD, 3600)
    past = datetime.now(timezone.utc) - timedelta(hours=5)
    mock_chain_fns["mychain"]["__ttl_set_at__"] = past.isoformat()
    expired = ttl_mod.list_expired_ttl(PASSWORD)
    assert "mychain" in expired
    assert "other" not in expired
