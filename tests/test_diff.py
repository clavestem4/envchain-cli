"""Tests for envchain.diff module."""
import pytest
from envchain.diff import diff_chains, format_diff


CHAIN_A = {"FOO": "bar", "BAZ": "qux", "SHARED": "same"}
CHAIN_B = {"FOO": "changed", "NEW": "value", "SHARED": "same"}


def test_diff_added():
    result = diff_chains(CHAIN_A, CHAIN_B)
    assert "NEW" in result["added"]
    assert result["added"]["NEW"] == "value"


def test_diff_removed():
    result = diff_chains(CHAIN_A, CHAIN_B)
    assert "BAZ" in result["removed"]
    assert result["removed"]["BAZ"] == "qux"


def test_diff_modified():
    result = diff_chains(CHAIN_A, CHAIN_B)
    assert "FOO" in result["modified"]
    assert result["modified"]["FOO"] == {"old": "bar", "new": "changed"}


def test_diff_unchanged():
    result = diff_chains(CHAIN_A, CHAIN_B)
    assert "SHARED" in result["unchanged"]


def test_diff_identical_chains():
    result = diff_chains(CHAIN_A, CHAIN_A)
    assert result["added"] == {}
    assert result["removed"] == {}
    assert result["modified"] == {}
    assert set(result["unchanged"].keys()) == set(CHAIN_A.keys())


def test_diff_empty_chains():
    result = diff_chains({}, {})
    assert all(len(v) == 0 for v in result.values())


def test_format_diff_contains_keys():
    diff = diff_chains(CHAIN_A, CHAIN_B)
    output = format_diff(diff)
    assert "+ NEW" in output
    assert "- BAZ" in output
    assert "~ FOO" in output
    assert "SHARED" in output


def test_format_diff_with_values():
    diff = diff_chains(CHAIN_A, CHAIN_B)
    output = format_diff(diff, show_values=True)
    assert "changed" in output
    assert "bar ->" in output


def test_format_diff_empty():
    diff = diff_chains({}, {})
    output = format_diff(diff)
    assert "(no variables)" in output
