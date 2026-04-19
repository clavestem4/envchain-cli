"""Tests for envchain.reminder."""
import pytest
from unittest.mock import patch, MagicMock
from envchain import reminder as R


@pytest.fixture
def mock_chain_fns():
    store = {}

    def fake_get(name, password=""):
        if name not in store:
            raise KeyError(name)
        return dict(store[name])

    def fake_add(name, data, password="", overwrite=False):
        store[name] = dict(data)

    def fake_names():
        return list(store.keys())

    with patch.object(R, "get_chain", side_effect=fake_get), \
         patch.object(R, "add_chain", side_effect=fake_add), \
         patch.object(R, "get_chain_names", side_effect=fake_names):
        store["mychain"] = {"KEY": "val"}
        yield store


def test_set_and_get_reminder(mock_chain_fns):
    R.set_reminder("mychain", "2099-12-31", note="review keys")
    result = R.get_reminder("mychain")
    assert result == {"date": "2099-12-31", "note": "review keys"}


def test_set_reminder_no_note(mock_chain_fns):
    R.set_reminder("mychain", "2099-01-01")
    result = R.get_reminder("mychain")
    assert result["note"] == ""


def test_set_reminder_invalid_date(mock_chain_fns):
    with pytest.raises(R.ReminderError):
        R.set_reminder("mychain", "31-12-2099")


def test_get_reminder_none(mock_chain_fns):
    result = R.get_reminder("mychain")
    assert result is None


def test_clear_reminder(mock_chain_fns):
    R.set_reminder("mychain", "2099-06-15")
    R.clear_reminder("mychain")
    assert R.get_reminder("mychain") is None


def test_clear_reminder_no_reminder(mock_chain_fns):
    R.clear_reminder("mychain")  # should not raise


def test_list_due_reminders(mock_chain_fns):
    mock_chain_fns["oldchain"] = {"X": "1"}
    R.set_reminder("mychain", "2099-01-01", note="future")
    R.set_reminder("oldchain", "2000-01-01", note="past")
    due = R.list_due_reminders()
    chains = [d["chain"] for d in due]
    assert "oldchain" in chains
    assert "mychain" not in chains


def test_list_due_reminders_empty(mock_chain_fns):
    due = R.list_due_reminders()
    assert due == []
