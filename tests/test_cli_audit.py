"""Tests for audit CLI commands."""

import pytest
from click.testing import CliRunner
from envchain.cli_audit import audit_group
from envchain.audit import log_event


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture(autouse=True)
def tmp_audit(tmp_path, monkeypatch):
    audit_file = tmp_path / "audit.log"
    monkeypatch.setenv("ENVCHAIN_AUDIT_LOG", str(audit_file))
    yield audit_file


def test_audit_log_empty(runner):
    result = runner.invoke(audit_group, ["log"])
    assert result.exit_code == 0
    assert "No audit events found" in result.output


def test_audit_log_shows_events(runner):
    log_event("add", "myproject", detail="KEY=val")
    log_event("get", "myproject")
    result = runner.invoke(audit_group, ["log"])
    assert result.exit_code == 0
    assert "ADD" in result.output
    assert "GET" in result.output
    assert "myproject" in result.output
    assert "KEY=val" in result.output


def test_audit_log_filter_by_chain(runner):
    log_event("add", "alpha")
    log_event("get", "beta")
    result = runner.invoke(audit_group, ["log", "--chain", "alpha"])
    assert result.exit_code == 0
    assert "alpha" in result.output
    assert "beta" not in result.output


def test_audit_clear_all(runner):
    log_event("add", "proj")
    log_event("get", "proj")
    result = runner.invoke(audit_group, ["clear"], input="y\n")
    assert result.exit_code == 0
    assert "2" in result.output


def test_audit_clear_by_chain(runner):
    log_event("add", "alpha")
    log_event("get", "beta")
    result = runner.invoke(audit_group, ["clear", "--chain", "alpha"], input="y\n")
    assert result.exit_code == 0
    assert "1" in result.output
    assert "alpha" in result.output


def test_audit_clear_aborted(runner):
    log_event("add", "proj")
    result = runner.invoke(audit_group, ["clear"], input="n\n")
    assert result.exit_code != 0 or "Aborted" in result.output
