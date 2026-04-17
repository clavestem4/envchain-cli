"""Tests for CLI diff commands."""
import pytest
from click.testing import CliRunner
from unittest.mock import patch
from envchain.cli_diff import diff_group


@pytest.fixture
def runner():
    return CliRunner()


CHAIN_DATA = {
    "dev": {"DB_HOST": "localhost", "DEBUG": "true", "SHARED": "x"},
    "prod": {"DB_HOST": "prod.db", "SECRET": "abc", "SHARED": "x"},
}


def _mock_get_chain(name, **kwargs):
    if name not in CHAIN_DATA:
        raise KeyError(name)
    return CHAIN_DATA[name]


def test_diff_show_basic(runner):
    with patch("envchain.cli_diff.get_chain", side_effect=_mock_get_chain):
        result = runner.invoke(diff_group, ["show", "dev", "prod"])
    assert result.exit_code == 0
    assert "dev -> prod" in result.output
    assert "change(s) detected" in result.output


def test_diff_show_added_removed(runner):
    with patch("envchain.cli_diff.get_chain", side_effect=_mock_get_chain):
        result = runner.invoke(diff_group, ["show", "dev", "prod"])
    assert "+ SECRET" in result.output
    assert "- DEBUG" in result.output


def test_diff_show_with_values(runner):
    with patch("envchain.cli_diff.get_chain", side_effect=_mock_get_chain):
        result = runner.invoke(diff_group, ["show", "dev", "prod", "--values"])
    assert "localhost" in result.output or "prod.db" in result.output


def test_diff_show_missing_chain_a(runner):
    with patch("envchain.cli_diff.get_chain", side_effect=_mock_get_chain):
        result = runner.invoke(diff_group, ["show", "missing", "prod"])
    assert result.exit_code != 0
    assert "not found" in result.output


def test_diff_show_missing_chain_b(runner):
    with patch("envchain.cli_diff.get_chain", side_effect=_mock_get_chain):
        result = runner.invoke(diff_group, ["show", "dev", "missing"])
    assert result.exit_code != 0
    assert "not found" in result.output
