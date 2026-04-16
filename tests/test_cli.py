import pytest
from click.testing import CliRunner
from unittest.mock import patch
from envchain.cli import cli

PASSWORD = "testpassword"
CHAIN = "myproject"
VARS = {"API_KEY": "abc123", "DEBUG": "true"}


@pytest.fixture
def runner():
    return CliRunner()


def test_add_and_list_chain(runner):
    with patch("envchain.cli.add_chain") as mock_add, \
         patch("envchain.cli.get_chain_names", return_value=[CHAIN]):
        result = runner.invoke(cli, [
            "add", CHAIN,
            "--password", PASSWORD,
            "-e", "API_KEY=abc123",
            "-e", "DEBUG=true"
        ])
        assert result.exit_code == 0
        assert "saved" in result.output
        mock_add.assert_called_once_with(CHAIN, {"API_KEY": "abc123", "DEBUG": "true"}, PASSWORD)

        result = runner.invoke(cli, ["list"])
        assert CHAIN in result.output


def test_add_invalid_env_format(runner):
    result = runner.invoke(cli, [
        "add", CHAIN,
        "--password", PASSWORD,
        "-e", "BADFORMAT"
    ])
    assert result.exit_code != 0


def test_get_chain(runner):
    with patch("envchain.cli.get_chain", return_value=VARS):
        result = runner.invoke(cli, ["get", CHAIN, "--password", PASSWORD])
        assert result.exit_code == 0
        assert "API_KEY=abc123" in result.output


def test_get_chain_export(runner):
    with patch("envchain.cli.get_chain", return_value=VARS):
        result = runner.invoke(cli, ["get", CHAIN, "--password", PASSWORD, "--export"])
        assert result.exit_code == 0
        assert "export API_KEY=abc123" in result.output


def test_remove_chain(runner):
    with patch("envchain.cli.remove_chain") as mock_remove:
        result = runner.invoke(cli, ["remove", CHAIN, "--yes"])
        assert result.exit_code == 0
        assert "removed" in result.output
        mock_remove.assert_called_once_with(CHAIN)


def test_list_empty(runner):
    with patch("envchain.cli.get_chain_names", return_value=[]):
        result = runner.invoke(cli, ["list"])
        assert "No chains found" in result.output
