"""Tests for envchain.schedule."""
import pytest
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock
from envchain.schedule import (
    set_schedule, get_schedule, clear_schedule, is_due, list_scheduled, SCHEDULE_KEY
)


@pytest.fixture
def mock_chain_fns():
    store = {}

    def fake_get(name, password):
        if name not in store:
            raise KeyError(name)
        return dict(store[name])

    def fake_add(name, chain, password, overwrite=False):
        store[name] = dict(chain)

    with patch("envchain.schedule.get_chain", side_effect=fake_get), \
         patch("envchain.schedule.add_chain", side_effect=fake_add):
        store["mychain"] = {"FOO": "bar"}
        yield store


def test_set_schedule(mock_chain_fns):
    set_schedule("mychain", "daily", "pass")
    assert mock_chain_fns["mychain"][SCHEDULE_KEY] == "daily"


def test_set_schedule_invalid_interval(mock_chain_fns):
    with pytest.raises(ValueError, match="Unsupported interval"):
        set_schedule("mychain", "monthly", "pass")


def test_set_schedule_overwrites_existing(mock_chain_fns):
    """Verify that setting a new schedule replaces the previous one."""
    mock_chain_fns["mychain"][SCHEDULE_KEY] = "daily"
    set_schedule("mychain", "weekly", "pass")
    assert mock_chain_fns["mychain"][SCHEDULE_KEY] == "weekly"


def test_get_schedule_returns_interval(mock_chain_fns):
    mock_chain_fns["mychain"][SCHEDULE_KEY] = "weekly"
    result = get_schedule("mychain", "pass")
    assert result == "weekly"


def test_get_schedule_returns_none_when_not_set(mock_chain_fns):
    result = get_schedule("mychain", "pass")
    assert result is None


def test_clear_schedule(mock_chain_fns):
    mock_chain_fns["mychain"][SCHEDULE_KEY] = "hourly"
    clear_schedule("mychain", "pass")
    assert SCHEDULE_KEY not in mock_chain_fns["mychain"]


def test_clear_schedule_no_existing_schedule(mock_chain_fns):
    """Clearing a schedule when none is set should not raise an error."""
    clear_schedule("mychain", "pass")
    assert SCHEDULE_KEY not in mock_chain_fns["mychain"]


def test_is_due_true(mock_chain_fns):
    mock_chain_fns["mychain"][SCHEDULE_KEY] = "hourly"
    past = datetime.utcnow() - timedelta(hours=2)
    assert is_due("mychain", "pass", past) is True


def test_is_due_false(mock_chain_fns):
    mock_chain_fns["mychain"][SCHEDULE_KEY] = "daily"
    recent = datetime.utcnow() - timedelta(hours=1)
    assert is_due("mychain", "pass", recent) is False


def test_is_due_no_schedule(mock_chain_fns):
    past = datetime.utcnow() - timedelta(days=10)
    assert is_due("mychain", "pass", past) is False


def test_list_scheduled(mock_chain_fns):
    mock_chain_fns["mychain"][SCHEDULE_KEY] = "weekly"
    mock_chain_fns["other"] = {"X": "1"}
    result = list_scheduled(["mychain", "other"], "pass")
    assert ("mychain", "weekly") in result
    assert all(n != "other" for n, _ in result)


def test_list_scheduled_empty(mock_chain_fns):
    """list_scheduled returns an empty list when no chains have a schedule."""
    result = list_scheduled(["mychain"], "pass")
    assert result == []
