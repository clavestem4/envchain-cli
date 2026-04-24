"""Tests for envchain.cli_trigger CLI commands."""

import pytest
from click.testing import CliRunner
from unittest.mock import patch
from envchain.cli_trigger import trigger_group
from envchain.trigger import TriggerError


@pytest.fixture
def runner():
    return CliRunner()


def test_trigger_set_success(runner):
    with patch("envchain.cli_trigger.set_trigger") as mock_set:
        result = runner.invoke(trigger_group, ["set", "mychain", "on_get", "echo hi"])
        assert result.exit_code == 0
        assert "Trigger set" in result.output
        mock_set.assert_called_once_with("mychain", "on_get", "echo hi")


def test_trigger_set_missing_chain(runner):
    with patch("envchain.cli_trigger.set_trigger", side_effect=KeyError("mychain")):
        result = runner.invoke(trigger_group, ["set", "mychain", "on_get", "echo hi"])
        assert result.exit_code == 1
        assert "not found" in result.output


def test_trigger_get_returns_command(runner):
    with patch("envchain.cli_trigger.get_trigger", return_value="echo accessed"):
        result = runner.invoke(trigger_group, ["get", "mychain", "on_get"])
        assert result.exit_code == 0
        assert "echo accessed" in result.output


def test_trigger_get_unset(runner):
    with patch("envchain.cli_trigger.get_trigger", return_value=None):
        result = runner.invoke(trigger_group, ["get", "mychain", "on_get"])
        assert result.exit_code == 0
        assert "No trigger set" in result.output


def test_trigger_remove_success(runner):
    with patch("envchain.cli_trigger.remove_trigger") as mock_rem:
        result = runner.invoke(trigger_group, ["remove", "mychain", "on_set"])
        assert result.exit_code == 0
        assert "removed" in result.output
        mock_rem.assert_called_once_with("mychain", "on_set")


def test_trigger_remove_not_set(runner):
    with patch("envchain.cli_trigger.remove_trigger", side_effect=TriggerError("No trigger set for event 'on_set'")):
        result = runner.invoke(trigger_group, ["remove", "mychain", "on_set"])
        assert result.exit_code == 1
        assert "Error" in result.output


def test_trigger_list_with_triggers(runner):
    with patch("envchain.cli_trigger.list_triggers", return_value={"on_get": "echo get", "on_set": "echo set"}):
        result = runner.invoke(trigger_group, ["list", "mychain"])
        assert result.exit_code == 0
        assert "on_get" in result.output
        assert "echo get" in result.output


def test_trigger_list_empty(runner):
    with patch("envchain.cli_trigger.list_triggers", return_value={}):
        result = runner.invoke(trigger_group, ["list", "mychain"])
        assert result.exit_code == 0
        assert "No triggers" in result.output


def test_trigger_find_results(runner):
    with patch("envchain.cli_trigger.find_chains_with_trigger", return_value=["chain_a", "chain_b"]):
        result = runner.invoke(trigger_group, ["find", "on_delete"])
        assert result.exit_code == 0
        assert "chain_a" in result.output
        assert "chain_b" in result.output


def test_trigger_find_no_results(runner):
    with patch("envchain.cli_trigger.find_chains_with_trigger", return_value=[]):
        result = runner.invoke(trigger_group, ["find", "on_delete"])
        assert result.exit_code == 0
        assert "No chains" in result.output
