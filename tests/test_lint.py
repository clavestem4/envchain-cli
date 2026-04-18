import pytest
from envchain.lint import lint_name, lint_value, lint_chain


def test_lint_name_valid():
    assert lint_name("DATABASE_URL") == []
    assert lint_name("API_KEY") == []


def test_lint_name_lowercase():
    warnings = lint_name("database_url")
    assert any("UPPER_SNAKE_CASE" in w for w in warnings)


def test_lint_name_mixed_case():
    warnings = lint_name("MyVar")
    assert any("UPPER_SNAKE_CASE" in w for w in warnings)


def test_lint_name_leading_underscore():
    warnings = lint_name("_PRIVATE")
    assert any("underscore" in w for w in warnings)


def test_lint_value_empty():
    warnings = lint_value("API_KEY", "")
    assert any("empty" in w for w in warnings)


def test_lint_value_placeholder_angle_brackets():
    warnings = lint_value("TOKEN", "<your-token>")
    assert any("template placeholder" in w for w in warnings)


def test_lint_value_shell_variable():
    warnings = lint_value("SECRET", "${MY_SECRET}")
    assert any("shell variable" in w for w in warnings)


def test_lint_value_suspicious_word():
    warnings = lint_value("API_KEY", "your-api-key")
    assert any("placeholder" in w for w in warnings)


def test_lint_value_clean():
    assert lint_value("API_KEY", "abc123xyz") == []


def test_lint_chain_mixed():
    chain = {
        "DATABASE_URL": "postgres://localhost/db",
        "api_token": "",
        "SECRET": "<your-secret>",
    }
    results = lint_chain(chain)
    assert "DATABASE_URL" not in results
    assert "api_token" in results
    assert "SECRET" in results


def test_lint_chain_all_clean():
    chain = {
        "DATABASE_URL": "postgres://localhost/db",
        "API_KEY": "realkey123",
    }
    assert lint_chain(chain) == {}
