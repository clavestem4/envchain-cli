"""Tests for CLI dependency commands."""

import pytest
from click.testing import CliRunner
from unittest.mock import patch
from envchain.cli_dependency import deps_group
from envchain.dependency import DependencyError


@pytest.fixture
def runner():
    return CliRunner()


def test_deps_set_success(runner):
    with patch("envchain.cli_dependency.set_dependencies") as mock_set:
        result = runner.invoke(deps_group, ["set", "app", "db", "cache", "--password", "pw"])
        mock_set.assert_called_once_with("app", ["db", "cache"], "pw")
        assert "set to" in result.output


def test_deps_set_error(runner):
    with patch("envchain.cli_dependency.set_dependencies", side_effect=DependencyError("bad")):
        result = runner.invoke(deps_group, ["set", "app", "missing", "--password", "pw"])
        assert result.exit_code == 1
        assert "Error" in result.output


def test_deps_get_with_deps(runner):
    with patch("envchain.cli_dependency.get_dependencies", return_value=["db", "cache"]):
        result = runner.invoke(deps_group, ["get", "app", "--password", "pw"])
        assert "db" in result.output
        assert "cache" in result.output


def test_deps_get_empty(runner):
    with patch("envchain.cli_dependency.get_dependencies", return_value=[]):
        result = runner.invoke(deps_group, ["get", "app", "--password", "pw"])
        assert "No dependencies" in result.output


def test_deps_clear_success(runner):
    with patch("envchain.cli_dependency.clear_dependencies") as mock_clear:
        result = runner.invoke(deps_group, ["clear", "app", "--password", "pw"])
        mock_clear.assert_called_once_with("app", "pw")
        assert "cleared" in result.output


def test_deps_order_success(runner):
    with patch("envchain.cli_dependency.resolve_order", return_value=["db", "app"]):
        result = runner.invoke(deps_group, ["order", "app", "db", "--password", "pw"])
        assert "db" in result.output
        assert "app" in result.output


def test_deps_order_circular(runner):
    with patch("envchain.cli_dependency.resolve_order", side_effect=DependencyError("Circular")):
        result = runner.invoke(deps_group, ["order", "app", "db", "--password", "pw"])
        assert result.exit_code == 1
        assert "Circular" in result.output
