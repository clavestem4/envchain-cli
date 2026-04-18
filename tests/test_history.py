"""Tests for envchain.history and envchain.cli_history."""

import pytest
from click.testing import CliRunner
from envchain.history import record_event, get_history, clear_history
from envchain.cli_history import history_group


@pytest.fixture
def tmp_hist(tmp_path):
    return str(tmp_path / "history.json")


@pytest.fixture
def runner():
    return CliRunner()


def test_record_event_creates_entry(tmp_hist):
    event = record_event("mychain", "add", variable="API_KEY", history_file=tmp_hist)
    assert event["chain"] == "mychain"
    assert event["action"] == "add"
    assert event["variable"] == "API_KEY"
    assert "timestamp" in event


def test_get_history_all(tmp_hist):
    record_event("a", "add", variable="X", history_file=tmp_hist)
    record_event("b", "delete", variable="Y", history_file=tmp_hist)
    events = get_history(history_file=tmp_hist)
    assert len(events) == 2


def test_get_history_filter_chain(tmp_hist):
    record_event("a", "add", variable="X", history_file=tmp_hist)
    record_event("b", "add", variable="Y", history_file=tmp_hist)
    events = get_history(chain="a", history_file=tmp_hist)
    assert len(events) == 1
    assert events[0]["chain"] == "a"


def test_get_history_filter_action(tmp_hist):
    record_event("a", "add", variable="X", history_file=tmp_hist)
    record_event("a", "delete", variable="X", history_file=tmp_hist)
    events = get_history(action="delete", history_file=tmp_hist)
    assert len(events) == 1
    assert events[0]["action"] == "delete"


def test_get_history_filter_chain_and_action(tmp_hist):
    """Filtering by both chain and action should narrow results correctly."""
    record_event("a", "add", variable="X", history_file=tmp_hist)
    record_event("a", "delete", variable="X", history_file=tmp_hist)
    record_event("b", "add", variable="Y", history_file=tmp_hist)
    events = get_history(chain="a", action="add", history_file=tmp_hist)
    assert len(events) == 1
    assert events[0]["chain"] == "a"
    assert events[0]["action"] == "add"


def test_clear_history_all(tmp_hist):
    record_event("a", "add", history_file=tmp_hist)
    record_event("b", "add", history_file=tmp_hist)
    removed = clear_history(history_file=tmp_hist)
    assert removed == 2
    assert get_history(history_file=tmp_hist) == []


def test_clear_history_by_chain(tmp_hist):
    record_event("a", "add", history_file=tmp_hist)
    record_event("b", "add", history_file=tmp_hist)
    removed = clear_history(chain="a", history_file=tmp_hist)
    assert removed == 1
    remaining = get_history(history_file=tmp_hist)
    assert len(remaining) == 1
    assert remaining[0]["chain"] == "b"


def test_get_history_empty(tmp_hist):
    assert get_history(history_file=tmp_hist) == []


# CLI tests


def test_cli_history_log_empty(runner, tmp_path, monkeypatch):
    hist_file = str(tmp_path / "h.json")
    monkeypatch.setattr("envchain.history.HISTORY_FILE", hist_file)
    result = runner.invoke(history_group, ["log"])
    assert result.exit_code == 0
    assert "No history found" in result.output


def test_cli_history_clear_with_yes(runner, tmp_path, monkeypatch):
    hist_file = str(tmp_path / "h.json")
    monkeypatch.setattr("envchain.history.HISTORY_FILE", hist_file)
    record_event("mychain", "add", history_file=hist_file)
    result = runner.invoke(history_group, ["clear", "--yes"])
    assert result.exit_code == 0
    assert "Removed 1" in result.output
