"""Tests for envchain.cli_lifecycle CLI commands."""

import pytest
from click.testing import CliRunner
from unittest.mock import patch
from envchain.cli_lifecycle import lifecycle_group
from envchain.lifecycle import LifecycleError


@pytest.fixture
def runner():
    return CliRunner()


def test_lifecycle_set_success(runner):
    with patch("envchain.cli_lifecycle.set_lifecycle") as mock_set:
        result = runner.invoke(
            lifecycle_group, ["set", "mychain", "active", "--password", "pw"]
        )
        mock_set.assert_called_once_with("mychain", "active", "pw")
        assert "set to 'active'" in result.output
        assert result.exit_code == 0


def test_lifecycle_set_missing_chain(runner):
    with patch("envchain.cli_lifecycle.set_lifecycle", side_effect=LifecycleError("not found")):
        result = runner.invoke(
            lifecycle_group, ["set", "ghost", "active", "--password", "pw"]
        )
        assert "Error" in result.output
        assert result.exit_code == 1


def test_lifecycle_get_value(runner):
    with patch("envchain.cli_lifecycle.get_lifecycle", return_value="deprecated"):
        result = runner.invoke(
            lifecycle_group, ["get", "mychain", "--password", "pw"]
        )
        assert "deprecated" in result.output
        assert result.exit_code == 0


def test_lifecycle_get_unset(runner):
    with patch("envchain.cli_lifecycle.get_lifecycle", return_value=None):
        result = runner.invoke(
            lifecycle_group, ["get", "mychain", "--password", "pw"]
        )
        assert "No lifecycle state" in result.output
        assert result.exit_code == 0


def test_lifecycle_clear_success(runner):
    with patch("envchain.cli_lifecycle.clear_lifecycle") as mock_clear:
        result = runner.invoke(
            lifecycle_group, ["clear", "mychain", "--password", "pw"]
        )
        mock_clear.assert_called_once_with("mychain", "pw")
        assert "cleared" in result.output
        assert result.exit_code == 0


def test_lifecycle_list_results(runner):
    with patch("envchain.cli_lifecycle.list_by_lifecycle", return_value=["a", "b"]):
        result = runner.invoke(
            lifecycle_group, ["list", "active", "--password", "pw"]
        )
        assert "a" in result.output
        assert "b" in result.output
        assert result.exit_code == 0


def test_lifecycle_list_empty(runner):
    with patch("envchain.cli_lifecycle.list_by_lifecycle", return_value=[]):
        result = runner.invoke(
            lifecycle_group, ["list", "archived", "--password", "pw"]
        )
        assert "No chains" in result.output
        assert result.exit_code == 0
