"""Tests for envchain.quota and envchain.cli_quota."""

import pytest
from unittest.mock import patch, MagicMock
from click.testing import CliRunner

from envchain.quota import (
    set_quota, get_quota, clear_quota, check_quota, list_over_quota, QuotaError, QUOTA_META_KEY
)
from envchain.cli_quota import quota_group


# --- Unit tests for quota.py ---

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

    with patch("envchain.quota.get_chain", side_effect=fake_get), \
         patch("envchain.quota.add_chain", side_effect=fake_add), \
         patch("envchain.quota.get_chain_names", side_effect=fake_names):
        store["mychain"] = {"KEY1": "val1", "KEY2": "val2"}
        yield store


def test_set_and_get_quota(mock_chain_fns):
    set_quota("mychain", 10, "pw")
    assert get_quota("mychain", "pw") == 10


def test_set_quota_invalid_raises(mock_chain_fns):
    with pytest.raises(QuotaError):
        set_quota("mychain", 0, "pw")


def test_get_quota_unset_returns_none(mock_chain_fns):
    assert get_quota("mychain", "pw") is None


def test_clear_quota(mock_chain_fns):
    set_quota("mychain", 5, "pw")
    clear_quota("mychain", "pw")
    assert get_quota("mychain", "pw") is None


def test_check_quota_within_limit(mock_chain_fns):
    set_quota("mychain", 5, "pw")
    info = check_quota("mychain", "pw")
    assert info["limit"] == 5
    assert info["used"] == 2
    assert info["remaining"] == 3
    assert info["exceeded"] is False


def test_check_quota_exceeded(mock_chain_fns):
    set_quota("mychain", 1, "pw")
    info = check_quota("mychain", "pw")
    assert info["exceeded"] is True


def test_check_quota_unlimited(mock_chain_fns):
    info = check_quota("mychain", "pw")
    assert info["limit"] is None
    assert info["remaining"] is None
    assert info["exceeded"] is False


def test_list_over_quota(mock_chain_fns):
    mock_chain_fns["small"] = {"A": "1", "B": "2", "C": "3", QUOTA_META_KEY: "2"}
    over = list_over_quota("pw")
    assert "small" in over
    assert "mychain" not in over


# --- CLI tests ---

@pytest.fixture
def runner():
    return CliRunner()


def test_quota_set_success(runner, mock_chain_fns):
    result = runner.invoke(quota_group, ["set", "mychain", "10", "--password", "pw"])
    assert result.exit_code == 0
    assert "set to 10" in result.output


def test_quota_get_shows_info(runner, mock_chain_fns):
    set_quota("mychain", 10, "pw")
    result = runner.invoke(quota_group, ["get", "mychain", "--password", "pw"])
    assert result.exit_code == 0
    assert "Limit" in result.output
    assert "Used" in result.output


def test_quota_clear_success(runner, mock_chain_fns):
    set_quota("mychain", 5, "pw")
    result = runner.invoke(quota_group, ["clear", "mychain", "--password", "pw"])
    assert result.exit_code == 0
    assert "cleared" in result.output


def test_quota_list_over_none(runner, mock_chain_fns):
    result = runner.invoke(quota_group, ["list-over", "--password", "pw"])
    assert result.exit_code == 0
    assert "No chains" in result.output
