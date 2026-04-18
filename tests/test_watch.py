"""Tests for envchain.watch drift detection."""
import pytest
from unittest.mock import patch
from envchain.watch import detect_drift, format_drift_report, has_drift, snapshot_chain


BASELINE = {"FOO": "bar", "BAZ": "qux"}


@pytest.fixture
def mock_get_chain():
    with patch("envchain.watch.get_chain") as m:
        yield m


def test_detect_drift_no_changes(mock_get_chain):
    mock_get_chain.return_value = {"FOO": "bar", "BAZ": "qux"}
    drift = detect_drift("mychain", "pw", BASELINE)
    assert drift == {"added": {}, "removed": {}, "modified": {}}
    assert not has_drift(drift)


def test_detect_drift_added(mock_get_chain):
    mock_get_chain.return_value = {"FOO": "bar", "BAZ": "qux", "NEW": "val"}
    drift = detect_drift("mychain", "pw", BASELINE)
    assert drift["added"] == {"NEW": "val"}
    assert drift["removed"] == {}
    assert drift["modified"] == {}
    assert has_drift(drift)


def test_detect_drift_removed(mock_get_chain):
    mock_get_chain.return_value = {"FOO": "bar"}
    drift = detect_drift("mychain", "pw", BASELINE)
    assert drift["removed"] == {"BAZ": "qux"}
    assert has_drift(drift)


def test_detect_drift_modified(mock_get_chain):
    mock_get_chain.return_value = {"FOO": "changed", "BAZ": "qux"}
    drift = detect_drift("mychain", "pw", BASELINE)
    assert drift["modified"] == {"FOO": {"before": "bar", "after": "changed"}}
    assert has_drift(drift)


def test_format_drift_no_drift(mock_get_chain):
    mock_get_chain.return_value = BASELINE.copy()
    drift = detect_drift("mychain", "pw", BASELINE)
    report = format_drift_report("mychain", drift)
    assert "No drift" in report


def test_format_drift_with_changes(mock_get_chain):
    mock_get_chain.return_value = {"FOO": "new", "EXTRA": "x"}
    drift = detect_drift("mychain", "pw", BASELINE)
    report = format_drift_report("mychain", drift)
    assert "+ EXTRA" in report
    assert "- BAZ" in report
    assert "~ FOO" in report


def test_snapshot_chain(mock_get_chain):
    mock_get_chain.return_value = {"A": "1"}
    snap = snapshot_chain("c", "pw")
    assert snap == {"A": "1"}
