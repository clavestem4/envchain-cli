"""Tests for CLI pin commands."""
import pytest
from click.testing import CliRunner
from unittest.mock import patch
from envchain.cli_pin import pin_group


@pytest.fixture
def runner():
    return CliRunner()


def test_pin_add_success(runner):
    with patch("envchain.cli_pin.pin_chain") as mock_pin:
        result = runner.invoke(pin_group, ["add", "mychain"])
    assert result.exit_code == 0
    assert "Pinned chain 'mychain'" in result.output
    mock_pin.assert_called_once_with("mychain")


def test_pin_add_missing_chain(runner):
    with patch("envchain.cli_pin.pin_chain", side_effect=KeyError("Chain 'x' does not exist")):
        result = runner.invoke(pin_group, ["add", "x"])
    assert result.exit_code == 1


def test_pin_remove_success(runner):
    with patch("envchain.cli_pin.unpin_chain") as mock_unpin:
        result = runner.invoke(pin_group, ["remove", "mychain"])
    assert result.exit_code == 0
    assert "Unpinned chain 'mychain'" in result.output


def test_pin_remove_not_pinned(runner):
    with patch("envchain.cli_pin.unpin_chain", side_effect=KeyError("not pinned")):
        result = runner.invoke(pin_group, ["remove", "x"])
    assert result.exit_code == 1


def test_pin_list_empty(runner):
    with patch("envchain.cli_pin.get_pinned", return_value=[]):
        result = runner.invoke(pin_group, ["list"])
    assert "No pinned chains" in result.output


def test_pin_list_shows_chains(runner):
    with patch("envchain.cli_pin.get_pinned", return_value=["a", "b"]):
        result = runner.invoke(pin_group, ["list"])
    assert "a" in result.output
    assert "b" in result.output
