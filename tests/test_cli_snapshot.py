"""Tests for envchain/cli_snapshot.py"""

import pytest
from click.testing import CliRunner
from unittest.mock import patch, MagicMock
from envchain.cli_snapshot import snapshot_group


@pytest.fixture
def runner():
    return CliRunner()


VARS = {"KEY": "val", "FOO": "bar"}


def test_snapshot_save(runner):
    with patch("envchain.cli_snapshot.get_chain", return_value=VARS) as mock_get, \
         patch("envchain.cli_snapshot.save_snapshot", return_value="snap1") as mock_save:
        result = runner.invoke(snapshot_group, ["save", "mychain", "pass", "--name", "snap1"])
        assert result.exit_code == 0
        assert "snap1" in result.output
        mock_get.assert_called_once_with("mychain", "pass")
        mock_save.assert_called_once_with("mychain", VARS, "snap1")


def test_snapshot_save_chain_error(runner):
    with patch("envchain.cli_snapshot.get_chain", side_effect=Exception("bad password")):
        result = runner.invoke(snapshot_group, ["save", "mychain", "wrongpass"])
        assert result.exit_code != 0
        assert "bad password" in result.output


def test_snapshot_list(runner):
    with patch("envchain.cli_snapshot.list_snapshots", return_value=["snap1", "snap2"]):
        result = runner.invoke(snapshot_group, ["list", "mychain"])
        assert result.exit_code == 0
        assert "snap1" in result.output
        assert "snap2" in result.output


def test_snapshot_list_empty(runner):
    with patch("envchain.cli_snapshot.list_snapshots", return_value=[]):
        result = runner.invoke(snapshot_group, ["list", "mychain"])
        assert result.exit_code == 0
        assert "No snapshots" in result.output


def test_snapshot_restore(runner):
    with patch("envchain.cli_snapshot.load_snapshot", return_value=VARS) as mock_load, \
         patch("envchain.cli_snapshot.add_chain") as mock_add:
        result = runner.invoke(snapshot_group, ["restore", "mychain", "snap1", "pass"])
        assert result.exit_code == 0
        assert "restored" in result.output
        mock_load.assert_called_once_with("mychain", "snap1")
        mock_add.assert_called_once_with("mychain", VARS, "pass", overwrite=False)


def test_snapshot_delete(runner):
    with patch("envchain.cli_snapshot.delete_snapshot") as mock_del:
        result = runner.invoke(snapshot_group, ["delete", "mychain", "snap1"])
        assert result.exit_code == 0
        assert "deleted" in result.output
        mock_del.assert_called_once_with("mychain", "snap1")


def test_snapshot_delete_missing(runner):
    with patch("envchain.cli_snapshot.delete_snapshot", side_effect=FileNotFoundError("not found")):
        result = runner.invoke(snapshot_group, ["delete", "mychain", "ghost"])
        assert result.exit_code != 0
        assert "not found" in result.output
