"""Tests for CLI priority commands."""

import pytest
from click.testing import CliRunner
from unittest.mock import patch
from envchain.cli_priority import priority_group
from envchain.priority import PriorityError


@pytest.fixture
def runner():
    return CliRunner()


def test_priority_set_success(runner):
    with patch("envchain.cli_priority.set_priority") as mock_set:
        result = runner.invoke(priority_group, ["set", "mychain", "3", "--password", "pw"])
        assert result.exit_code == 0
        assert "set to 3" in result.output
        mock_set.assert_called_once_with("mychain", 3, "pw")


def test_priority_set_error(runner):
    with patch("envchain.cli_priority.set_priority", side_effect=KeyError("mychain")):
        result = runner.invoke(priority_group, ["set", "mychain", "3", "--password", "pw"])
        assert result.exit_code == 1


def test_priority_get_value(runner):
    with patch("envchain.cli_priority.get_priority", return_value=5):
        result = runner.invoke(priority_group, ["get", "mychain", "--password", "pw"])
        assert result.exit_code == 0
        assert "5" in result.output


def test_priority_get_unset(runner):
    with patch("envchain.cli_priority.get_priority", return_value=None):
        result = runner.invoke(priority_group, ["get", "mychain", "--password", "pw"])
        assert "no priority" in result.output


def test_priority_clear_success(runner):
    with patch("envchain.cli_priority.clear_priority") as mock_clear:
        result = runner.invoke(priority_group, ["clear", "mychain", "--password", "pw"])
        assert result.exit_code == 0
        assert "cleared" in result.output


def test_priority_clear_not_set(runner):
    with patch("envchain.cli_priority.clear_priority", side_effect=PriorityError("no priority")):
        result = runner.invoke(priority_group, ["clear", "mychain", "--password", "pw"])
        assert result.exit_code == 1


def test_priority_list(runner):
    with patch("envchain.cli_priority.list_by_priority", return_value=[("alpha", 1), ("beta", None)]):
        result = runner.invoke(priority_group, ["list", "--password", "pw"])
        assert "alpha: 1" in result.output
        assert "beta: (unset)" in result.output
