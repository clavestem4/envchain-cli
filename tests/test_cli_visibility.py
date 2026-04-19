"""Tests for envchain.cli_visibility CLI commands."""

import pytest
from click.testing import CliRunner
from unittest.mock import patch
from envchain.cli_visibility import visibility_group


@pytest.fixture
def runner():
    return CliRunner()


def test_visibility_set_success(runner):
    with patch("envchain.cli_visibility.set_visibility") as mock_set:
        result = runner.invoke(visibility_group, ["set", "mychain", "public", "--password", "pw"])
        assert result.exit_code == 0
        assert "set to 'public'" in result.output
        mock_set.assert_called_once_with("mychain", "public", "pw")


def test_visibility_set_missing_chain(runner):
    with patch("envchain.cli_visibility.set_visibility", side_effect=KeyError("mychain")):
        result = runner.invoke(visibility_group, ["set", "mychain", "private", "--password", "pw"])
        assert result.exit_code != 0
        assert "not found" in result.output


def test_visibility_get_value(runner):
    with patch("envchain.cli_visibility.get_visibility", return_value="shared"):
        result = runner.invoke(visibility_group, ["get", "mychain", "--password", "pw"])
        assert result.exit_code == 0
        assert "shared" in result.output


def test_visibility_get_missing_chain(runner):
    with patch("envchain.cli_visibility.get_visibility", side_effect=KeyError("mychain")):
        result = runner.invoke(visibility_group, ["get", "mychain", "--password", "pw"])
        assert result.exit_code != 0


def test_visibility_clear_success(runner):
    with patch("envchain.cli_visibility.clear_visibility") as mock_clear:
        result = runner.invoke(visibility_group, ["clear", "mychain", "--password", "pw"])
        assert result.exit_code == 0
        assert "cleared" in result.output
        mock_clear.assert_called_once_with("mychain", "pw")


def test_visibility_list_results(runner):
    with patch("envchain.cli_visibility.list_by_visibility", return_value=["alpha", "beta"]):
        result = runner.invoke(visibility_group, ["list", "public", "--password", "pw"])
        assert result.exit_code == 0
        assert "alpha" in result.output
        assert "beta" in result.output


def test_visibility_list_empty(runner):
    with patch("envchain.cli_visibility.list_by_visibility", return_value=[]):
        result = runner.invoke(visibility_group, ["list", "shared", "--password", "pw"])
        assert result.exit_code == 0
        assert "No chains" in result.output
