"""Tests for envchain.cli_permission CLI commands."""

import pytest
from click.testing import CliRunner
from unittest.mock import patch
from envchain.cli_permission import permission_group
from envchain.permission import PermissionError


@pytest.fixture
def runner():
    return CliRunner()


def test_permission_set_success(runner):
    with patch("envchain.cli_permission.set_permission") as mock_set:
        result = runner.invoke(permission_group, ["set", "mychain", "alice", "read", "write"])
        assert result.exit_code == 0
        assert "alice" in result.output
        mock_set.assert_called_once_with("mychain", "alice", ["read", "write"])


def test_permission_set_invalid(runner):
    with patch("envchain.cli_permission.set_permission", side_effect=PermissionError("Invalid permissions: delete")):
        result = runner.invoke(permission_group, ["set", "mychain", "alice", "delete"])
        assert result.exit_code == 1
        assert "Invalid permissions" in result.output


def test_permission_set_missing_chain(runner):
    with patch("envchain.cli_permission.set_permission", side_effect=KeyError("mychain")):
        result = runner.invoke(permission_group, ["set", "mychain", "alice", "read"])
        assert result.exit_code == 1
        assert "not found" in result.output


def test_permission_get_with_perms(runner):
    with patch("envchain.cli_permission.get_permission", return_value=["read", "write"]):
        result = runner.invoke(permission_group, ["get", "mychain", "alice"])
        assert result.exit_code == 0
        assert "alice" in result.output
        assert "read" in result.output


def test_permission_get_empty(runner):
    with patch("envchain.cli_permission.get_permission", return_value=[]):
        result = runner.invoke(permission_group, ["get", "mychain", "alice"])
        assert result.exit_code == 0
        assert "no permissions" in result.output


def test_permission_revoke_success(runner):
    with patch("envchain.cli_permission.revoke_permission") as mock_rev:
        result = runner.invoke(permission_group, ["revoke", "mychain", "alice"])
        assert result.exit_code == 0
        assert "Revoked" in result.output
        mock_rev.assert_called_once_with("mychain", "alice")


def test_permission_list_success(runner):
    with patch("envchain.cli_permission.list_permissions", return_value={"alice": ["read"], "bob": ["write"]}):
        result = runner.invoke(permission_group, ["list", "mychain"])
        assert result.exit_code == 0
        assert "alice" in result.output
        assert "bob" in result.output


def test_permission_list_empty(runner):
    with patch("envchain.cli_permission.list_permissions", return_value={}):
        result = runner.invoke(permission_group, ["list", "mychain"])
        assert result.exit_code == 0
        assert "No permissions" in result.output


def test_permission_find_success(runner):
    with patch("envchain.cli_permission.find_chains_for_user", return_value=["mychain", "other"]):
        result = runner.invoke(permission_group, ["find", "alice"])
        assert result.exit_code == 0
        assert "mychain" in result.output


def test_permission_find_none(runner):
    with patch("envchain.cli_permission.find_chains_for_user", return_value=[]):
        result = runner.invoke(permission_group, ["find", "ghost"])
        assert result.exit_code == 0
        assert "No chains found" in result.output
