import pytest
from click.testing import CliRunner
from unittest.mock import patch
from envchain.cli_alias import alias_group


@pytest.fixture
def runner():
    return CliRunner()


def test_alias_set_success(runner):
    with patch("envchain.cli_alias.set_alias") as mock_set:
        result = runner.invoke(alias_group, ["set", "p", "prod"])
    assert result.exit_code == 0
    assert "'p' -> 'prod'" in result.output
    mock_set.assert_called_once_with("p", "prod")


def test_alias_set_missing_target(runner):
    with patch("envchain.cli_alias.set_alias", side_effect=KeyError("Target chain 'x' does not exist.")):
        result = runner.invoke(alias_group, ["set", "p", "x"])
    assert result.exit_code == 1
    assert "Error" in result.output


def test_alias_remove_success(runner):
    with patch("envchain.cli_alias.remove_alias") as mock_rm:
        result = runner.invoke(alias_group, ["remove", "p"])
    assert result.exit_code == 0
    assert "removed" in result.output


def test_alias_remove_missing(runner):
    with patch("envchain.cli_alias.remove_alias", side_effect=KeyError("Alias 'p' does not exist.")):
        result = runner.invoke(alias_group, ["remove", "p"])
    assert result.exit_code == 1


def test_alias_resolve(runner):
    with patch("envchain.cli_alias.resolve_alias", return_value="prod"):
        result = runner.invoke(alias_group, ["resolve", "p"])
    assert result.exit_code == 0
    assert "prod" in result.output


def test_alias_list_empty(runner):
    with patch("envchain.cli_alias.list_aliases", return_value={}):
        result = runner.invoke(alias_group, ["list"])
    assert "No aliases" in result.output


def test_alias_list_with_entries(runner):
    with patch("envchain.cli_alias.list_aliases", return_value={"p": "prod", "s": "staging"}):
        result = runner.invoke(alias_group, ["list"])
    assert "p -> prod" in result.output
    assert "s -> staging" in result.output
