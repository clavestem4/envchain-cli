"""Tests for template rendering feature."""
import pytest
from unittest.mock import patch
from click.testing import CliRunner
from envchain.template import render_template, render_template_file
from envchain.cli_template import template_group

FAKE_CHAIN = {"HOST": "localhost", "PORT": "5432", "USER": "admin"}


@pytest.fixture
def mock_get_chain():
    with patch("envchain.template.get_chain", return_value=FAKE_CHAIN) as m:
        yield m


def test_render_template_basic(mock_get_chain):
    result = render_template("Connect to $HOST:$PORT", "mychain", "pass")
    assert result == "Connect to localhost:5432"


def test_render_template_braces(mock_get_chain):
    result = render_template("User: ${USER}@${HOST}", "mychain", "pass")
    assert result == "User: admin@localhost"


def test_render_template_missing_strict(mock_get_chain):
    with pytest.raises(KeyError):
        render_template("Value: $MISSING", "mychain", "pass", strict=True)


def test_render_template_missing_loose(mock_get_chain):
    result = render_template("Value: $MISSING", "mychain", "pass", strict=False)
    assert "$MISSING" in result


def test_render_template_no_substitutions(mock_get_chain):
    """Template with no variables should be returned unchanged."""
    result = render_template("no variables here", "mychain", "pass")
    assert result == "no variables here"


def test_render_template_file(mock_get_chain, tmp_path):
    tpl = tmp_path / "tmpl.txt"
    tpl.write_text("host=$HOST port=$PORT")
    result = render_template_file(str(tpl), "mychain", "pass")
    assert result == "host=localhost port=5432"


@pytest.fixture
def runner():
    return CliRunner()


def test_cli_render_string(runner, mock_get_chain):
    result = runner.invoke(
        template_group,
        ["render", "mychain", "--password", "pass", "--string", "$HOST:$PORT"],
    )
    assert result.exit_code == 0
    assert "localhost:5432" in result.output


def test_cli_render_file(runner, mock_get_chain, tmp_path):
    tpl = tmp_path / "t.txt"
    tpl.write_text("user=$USER")
    result = runner.invoke(
        template_group,
        ["render", "mychain", "--password", "pass", "--file", str(tpl)],
    )
    assert result.exit_code == 0
    assert "user=admin" in result.output


def test_cli_render_both_options_error(runner, mock_get_chain):
    result = runner.invoke(
        template_group,
        ["render", "mychain", "--password", "pass", "--string", "x", "--file", "y"],
    )
    assert result.exit_code != 0


def test_cli_render_no_options_error(runner, mock_get_chain):
    result = runner.invoke(
        template_group,
        ["render", "mychain", "--password", "pass"],
    )
    assert result.exit_code != 0


def test_cli_render_missing_file_error(runner, mock_get_chain, tmp_path):
    """Rendering a non-existent file should result in a non-zero exit code."""
    missing = tmp_path / "nonexistent.txt"
    result = runner.invoke(
        template_group,
        ["render", "mychain", "--password", "pass", "--file", str(missing)],
    )
    assert result.exit_code != 0
