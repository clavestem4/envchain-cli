"""Tests for envchain.cli_criticality CLI commands."""

import pytest
from click.testing import CliRunner
from unittest.mock import patch
from envchain.cli_criticality import criticality_group
from envchain.criticality import CriticalityError


@pytest.fixture
def runner():
    return CliRunner()


def test_criticality_set_success(runner):
    with patch("envchain.cli_criticality.set_criticality") as mock_set:
        result = runner.invoke(
            criticality_group,
            ["set", "mychain", "high", "--password", "secret"],
        )
        assert result.exit_code == 0
        assert "set to 'high'" in result.output
        mock_set.assert_called_once_with("mychain", "high", "secret")


def test_criticality_set_missing_chain(runner):
    with patch("envchain.cli_criticality.set_criticality", side_effect=KeyError("mychain")):
        result = runner.invoke(
            criticality_group,
            ["set", "mychain", "low", "--password", "secret"],
        )
        assert result.exit_code == 1
        assert "not found" in result.output


def test_criticality_get_value(runner):
    with patch("envchain.cli_criticality.get_criticality", return_value="critical"):
        result = runner.invoke(
            criticality_group,
            ["get", "mychain", "--password", "secret"],
        )
        assert result.exit_code == 0
        assert "critical" in result.output


def test_criticality_get_unset(runner):
    with patch("envchain.cli_criticality.get_criticality", return_value=None):
        result = runner.invoke(
            criticality_group,
            ["get", "mychain", "--password", "secret"],
        )
        assert result.exit_code == 0
        assert "No criticality set" in result.output


def test_criticality_clear_success(runner):
    with patch("envchain.cli_criticality.clear_criticality") as mock_clear:
        result = runner.invoke(
            criticality_group,
            ["clear", "mychain", "--password", "secret"],
        )
        assert result.exit_code == 0
        assert "cleared" in result.output
        mock_clear.assert_called_once_with("mychain", "secret")


def test_criticality_list_results(runner):
    with patch("envchain.cli_criticality.list_by_criticality", return_value=["chain1", "chain2"]):
        result = runner.invoke(
            criticality_group,
            ["list", "high", "--password", "secret"],
        )
        assert result.exit_code == 0
        assert "chain1" in result.output
        assert "chain2" in result.output


def test_criticality_list_empty(runner):
    with patch("envchain.cli_criticality.list_by_criticality", return_value=[]):
        result = runner.invoke(
            criticality_group,
            ["list", "medium", "--password", "secret"],
        )
        assert result.exit_code == 0
        assert "No chains" in result.output
