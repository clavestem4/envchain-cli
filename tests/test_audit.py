"""Tests for envchain.audit module."""

import json
import os
import pytest
from pathlib import Path

from envchain.audit import log_event, read_events, clear_events


@pytest.fixture(autouse=True)
def tmp_audit(tmp_path, monkeypatch):
    audit_file = tmp_path / "audit.log"
    monkeypatch.setenv("ENVCHAIN_AUDIT_LOG", str(audit_file))
    yield audit_file


def test_log_event_creates_file(tmp_audit):
    log_event("add", "myproject")
    assert tmp_audit.exists()


def test_log_event_structure(tmp_audit):
    log_event("add", "myproject", detail="KEY=VALUE")
    events = read_events()
    assert len(events) == 1
    e = events[0]
    assert e["action"] == "add"
    assert e["chain"] == "myproject"
    assert e["detail"] == "KEY=VALUE"
    assert "timestamp" in e


def test_log_multiple_events(tmp_audit):
    log_event("add", "proj1")
    log_event("get", "proj2")
    log_event("remove", "proj1")
    events = read_events()
    assert len(events) == 3


def test_read_events_filter_by_chain(tmp_audit):
    log_event("add", "alpha")
    log_event("get", "beta")
    log_event("add", "alpha")
    events = read_events(chain_name="alpha")
    assert len(events) == 2
    assert all(e["chain"] == "alpha" for e in events)


def test_read_events_no_log_returns_empty(tmp_audit):
    events = read_events()
    assert events == []


def test_clear_all_events(tmp_audit):
    log_event("add", "proj1")
    log_event("get", "proj2")
    removed = clear_events()
    assert removed == 2
    assert read_events() == []


def test_clear_events_by_chain(tmp_audit):
    log_event("add", "alpha")
    log_event("get", "beta")
    log_event("add", "alpha")
    removed = clear_events(chain_name="alpha")
    assert removed == 2
    remaining = read_events()
    assert len(remaining) == 1
    assert remaining[0]["chain"] == "beta"


def test_clear_events_no_file_returns_zero(tmp_audit):
    assert clear_events() == 0
