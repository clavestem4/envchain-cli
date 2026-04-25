"""Tests for CLI trust commands."""

import pytest
from click.testing import CliRunner
from unittest.mock import patch
from envchain.cli_trust import trust_group


@pytest.fixture
def runner():
    return CliRunner()


def test_trust_set_success(runner):
    with patch("envchain.cli_trust.set_trust") as mock_set:
        result = runner.invoke(
            trust_group, ["set", "mychain", "high", "--password", "secret"]
        )
        mock_set.assert_called_once_with("mychain", "high", "secret")
        assert result.exit_code == 0
        assert "set to 'high'" in result.output


def test_trust_set_missing_chain(runner):
    with patch("envchain.cli_trust.set_trust", side_effect=KeyError("Chain not found")):
        result = runner.invoke(
            trust_group, ["set", "missing", "low", "--password", "secret"]
        )
        assert result.exit_code == 1
        assert "Error" in result.output


def test_trust_get_value(runner):
    with patch("envchain.cli_trust.get_trust", return_value="verified"):
        result = runner.invoke(
            trust_group, ["get", "mychain", "--password", "secret"]
        )
        assert result.exit_code == 0
        assert "verified" in result.output


def test_trust_get_unset(runner):
    with patch("envchain.cli_trust.get_trust", return_value=None):
        result = runner.invoke(
            trust_group, ["get", "mychain", "--password", "secret"]
        )
        assert result.exit_code == 0
        assert "No trust level set" in result.output


def test_trust_clear_success(runner):
    with patch("envchain.cli_trust.clear_trust") as mock_clear:
        result = runner.invoke(
            trust_group, ["clear", "mychain", "--password", "secret"]
        )
        mock_clear.assert_called_once_with("mychain", "secret")
        assert result.exit_code == 0
        assert "cleared" in result.output


def test_trust_list_results(runner):
    with patch("envchain.cli_trust.list_by_trust", return_value=["chain1", "chain2"]):
        result = runner.invoke(
            trust_group, ["list", "medium", "--password", "secret"]
        )
        assert result.exit_code == 0
        assert "chain1" in result.output
        assert "chain2" in result.output


def test_trust_list_empty(runner):
    with patch("envchain.cli_trust.list_by_trust", return_value=[]):
        result = runner.invoke(
            trust_group, ["list", "untrusted", "--password", "secret"]
        )
        assert result.exit_code == 0
        assert "No chains" in result.output
