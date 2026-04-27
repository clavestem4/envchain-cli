"""Tests for envchain.cli_lineage."""

import pytest
from click.testing import CliRunner
from unittest.mock import patch
from envchain.cli_lineage import lineage_group
from envchain.lineage import LineageError


@pytest.fixture()
def runner():
    return CliRunner()


def invoke(runner, args, input_text="test-pass\n"):
    return runner.invoke(lineage_group, args, input=input_text)


def test_set_parent_success(runner):
    with patch("envchain.cli_lineage.set_parent") as mock_set:
        result = invoke(runner, ["set-parent", "beta", "alpha"])
    mock_set.assert_called_once_with("beta", "alpha", "test-pass")
    assert "Set 'alpha' as parent of 'beta'" in result.output
    assert result.exit_code == 0


def test_set_parent_error(runner):
    with patch("envchain.cli_lineage.set_parent", side_effect=LineageError("bad")):
        result = invoke(runner, ["set-parent", "beta", "ghost"])
    assert "Error: bad" in result.output
    assert result.exit_code == 1


def test_get_parent_set(runner):
    with patch("envchain.cli_lineage.get_parent", return_value="alpha"):
        result = invoke(runner, ["get-parent", "beta"])
    assert "alpha" in result.output
    assert result.exit_code == 0


def test_get_parent_unset(runner):
    with patch("envchain.cli_lineage.get_parent", return_value=None):
        result = invoke(runner, ["get-parent", "beta"])
    assert "No parent" in result.output


def test_clear_parent_success(runner):
    with patch("envchain.cli_lineage.clear_parent") as mock_clear:
        result = invoke(runner, ["clear-parent", "beta"])
    mock_clear.assert_called_once()
    assert "cleared" in result.output


def test_children_found(runner):
    with patch("envchain.cli_lineage.get_children", return_value=["beta", "gamma"]):
        result = invoke(runner, ["children", "alpha"])
    assert "beta" in result.output
    assert "gamma" in result.output


def test_children_none(runner):
    with patch("envchain.cli_lineage.get_children", return_value=[]):
        result = invoke(runner, ["children", "alpha"])
    assert "No children" in result.output


def test_ancestors_found(runner):
    with patch("envchain.cli_lineage.get_ancestors", return_value=["beta", "alpha"]):
        result = invoke(runner, ["ancestors", "gamma"])
    assert "beta" in result.output
    assert "alpha" in result.output


def test_ancestors_none(runner):
    with patch("envchain.cli_lineage.get_ancestors", return_value=[]):
        result = invoke(runner, ["ancestors", "alpha"])
    assert "No ancestors" in result.output
