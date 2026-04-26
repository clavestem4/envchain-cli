import pytest
from click.testing import CliRunner
from unittest.mock import patch
from envchain.cli_sensitivity import sensitivity_group


@pytest.fixture
def runner():
    return CliRunner()


def test_sensitivity_set_success(runner):
    with patch("envchain.cli_sensitivity.get_chain") as mock_get, \
         patch("envchain.cli_sensitivity.add_chain") as mock_add:
        mock_get.return_value = {"KEY": "val"}
        result = runner.invoke(
            sensitivity_group,
            ["set", "mychain", "confidential", "--password", "pass"],
        )
        assert result.exit_code == 0
        assert "confidential" in result.output


def test_sensitivity_set_invalid_level(runner):
    with patch("envchain.cli_sensitivity.get_chain") as mock_get:
        mock_get.return_value = {"KEY": "val"}
        result = runner.invoke(
            sensitivity_group,
            ["set", "mychain", "bogus", "--password", "pass"],
        )
        assert result.exit_code != 0
        assert "Error" in result.output


def test_sensitivity_set_missing_chain(runner):
    with patch("envchain.cli_sensitivity.get_chain", side_effect=KeyError("mychain")):
        result = runner.invoke(
            sensitivity_group,
            ["set", "mychain", "secret", "--password", "pass"],
        )
        assert result.exit_code != 0
        assert "Error" in result.output


def test_sensitivity_get_value(runner):
    with patch("envchain.cli_sensitivity.get_chain") as mock_get:
        mock_get.return_value = {"KEY": "val", "__sensitivity__": "internal"}
        result = runner.invoke(
            sensitivity_group,
            ["get", "mychain", "--password", "pass"],
        )
        assert result.exit_code == 0
        assert "internal" in result.output


def test_sensitivity_get_unset(runner):
    with patch("envchain.cli_sensitivity.get_chain") as mock_get:
        mock_get.return_value = {"KEY": "val"}
        result = runner.invoke(
            sensitivity_group,
            ["get", "mychain", "--password", "pass"],
        )
        assert result.exit_code == 0
        assert "not set" in result.output


def test_sensitivity_list_results(runner):
    with patch("envchain.cli_sensitivity.get_chain_names", return_value=["a", "b"]), \
         patch("envchain.cli_sensitivity.get_chain") as mock_get:
        mock_get.side_effect = lambda name, pw: (
            {"__sensitivity__": "public"} if name == "a" else {}
        )
        result = runner.invoke(
            sensitivity_group,
            ["list", "public", "--password", "pass"],
        )
        assert result.exit_code == 0
        assert "a" in result.output
        assert "b" not in result.output
