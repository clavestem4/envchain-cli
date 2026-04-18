"""Tests for CLI notes commands."""
import pytest
from click.testing import CliRunner
from unittest.mock import patch
from envchain.cli_notes import notes_group


@pytest.fixture
def runner():
    return CliRunner()


def test_notes_set_success(runner):
    with patch("envchain.cli_notes.set_note") as mock_set:
        result = runner.invoke(notes_group, ["set", "mychain", "A note", "--password", "secret"])
        mock_set.assert_called_once_with("mychain", "A note", "secret")
        assert "Note set for chain 'mychain'" in result.output


def test_notes_set_missing_chain(runner):
    with patch("envchain.cli_notes.set_note", side_effect=KeyError("mychain")):
        result = runner.invoke(notes_group, ["set", "mychain", "A note", "--password", "secret"])
        assert result.exit_code == 1


def test_notes_get_with_note(runner):
    with patch("envchain.cli_notes.get_note", return_value="My description"):
        result = runner.invoke(notes_group, ["get", "mychain", "--password", "secret"])
        assert "My description" in result.output


def test_notes_get_empty(runner):
    with patch("envchain.cli_notes.get_note", return_value=""):
        result = runner.invoke(notes_group, ["get", "mychain", "--password", "secret"])
        assert "No note set" in result.output


def test_notes_get_missing_chain(runner):
    with patch("envchain.cli_notes.get_note", side_effect=KeyError("mychain")):
        result = runner.invoke(notes_group, ["get", "mychain", "--password", "secret"])
        assert result.exit_code == 1


def test_notes_clear_success(runner):
    with patch("envchain.cli_notes.clear_note") as mock_clear:
        result = runner.invoke(notes_group, ["clear", "mychain", "--password", "secret"])
        mock_clear.assert_called_once_with("mychain", "secret")
        assert "Note cleared" in result.output
