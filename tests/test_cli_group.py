import pytest
from click.testing import CliRunner
from unittest.mock import patch
from envchain.cli_group import group_cmd
from envchain.env_group import GroupError


@pytest.fixture
def runner():
    return CliRunner()


def test_group_create_success(runner):
    with patch("envchain.cli_group.create_group") as mock_create:
        result = runner.invoke(group_cmd, ["create", "mygroup", "dev", "prod"])
        mock_create.assert_called_once_with("mygroup", ["dev", "prod"])
        assert "created" in result.output


def test_group_create_missing_chain(runner):
    with patch("envchain.cli_group.create_group", side_effect=GroupError("prod not found")):
        result = runner.invoke(group_cmd, ["create", "mygroup", "dev", "prod"])
        assert result.exit_code == 1
        assert "prod not found" in result.output


def test_group_show_success(runner):
    with patch("envchain.cli_group.get_group", return_value=["dev", "staging"]):
        result = runner.invoke(group_cmd, ["show", "mygroup"])
        assert "dev" in result.output
        assert "staging" in result.output


def test_group_show_missing(runner):
    with patch("envchain.cli_group.get_group", side_effect=GroupError("Group 'x' not found")):
        result = runner.invoke(group_cmd, ["show", "x"])
        assert result.exit_code == 1


def test_group_delete_success(runner):
    with patch("envchain.cli_group.delete_group") as mock_del:
        result = runner.invoke(group_cmd, ["delete", "mygroup"])
        mock_del.assert_called_once_with("mygroup")
        assert "deleted" in result.output


def test_group_list_empty(runner):
    with patch("envchain.cli_group.list_groups", return_value={}):
        result = runner.invoke(group_cmd, ["list"])
        assert "No groups" in result.output


def test_group_list_with_groups(runner):
    with patch("envchain.cli_group.list_groups", return_value={"g1": ["a", "b"]}):
        result = runner.invoke(group_cmd, ["list"])
        assert "g1" in result.output
        assert "a" in result.output
