"""Tests for envchain.export module."""

import pytest
from envchain.export import export_chain, export_bash, export_fish, export_dotenv, SUPPORTED_FORMATS


SAMPLE_VARS = {
    "API_KEY": "abc123",
    "DB_URL": "postgres://localhost/mydb",
}


def test_export_bash_format():
    result = export_bash(SAMPLE_VARS)
    assert 'export API_KEY="abc123"' in result
    assert 'export DB_URL="postgres://localhost/mydb"' in result


def test_export_fish_format():
    result = export_fish(SAMPLE_VARS)
    assert 'set -x API_KEY "abc123"' in result
    assert 'set -x DB_URL "postgres://localhost/mydb"' in result


def test_export_dotenv_format():
    result = export_dotenv(SAMPLE_VARS)
    assert 'API_KEY="abc123"' in result
    assert 'DB_URL="postgres://localhost/mydb"' in result
    assert "export" not in result


def test_export_chain_bash():
    result = export_chain(SAMPLE_VARS, fmt="bash")
    assert result == export_bash(SAMPLE_VARS)


def test_export_chain_fish():
    result = export_chain(SAMPLE_VARS, fmt="fish")
    assert result == export_fish(SAMPLE_VARS)


def test_export_chain_dotenv():
    result = export_chain(SAMPLE_VARS, fmt="dotenv")
    assert result == export_dotenv(SAMPLE_VARS)


def test_export_chain_default_is_bash():
    result = export_chain(SAMPLE_VARS)
    assert result == export_bash(SAMPLE_VARS)


def test_export_chain_invalid_format():
    with pytest.raises(ValueError, match="Unsupported format"):
        export_chain(SAMPLE_VARS, fmt="powershell")


def test_export_escapes_double_quotes():
    vars_with_quotes = {"MSG": 'say "hello"'}
    result = export_bash(vars_with_quotes)
    assert '\\"' in result


def test_export_empty_vars():
    result = export_chain({}, fmt="bash")
    assert result == ""


def test_supported_formats_list():
    assert "bash" in SUPPORTED_FORMATS
    assert "fish" in SUPPORTED_FORMATS
    assert "dotenv" in SUPPORTED_FORMATS
