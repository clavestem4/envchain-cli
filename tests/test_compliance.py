"""Tests for envchain.compliance."""

import pytest
from unittest.mock import MagicMock
from envchain.compliance import (
    set_compliance,
    remove_compliance,
    get_compliance,
    list_by_compliance,
    ComplianceError,
)


@pytest.fixture()
def mock_chain_fns():
    store = {}

    def fake_get(name, password=""):
        if name not in store:
            raise KeyError(f"Chain '{name}' not found.")
        return dict(store[name])

    def fake_add(name, data, password="", overwrite=False):
        store[name] = dict(data)

    def fake_names():
        return list(store.keys())

    store["mychain"] = {"API_KEY": "secret"}
    return fake_get, fake_add, fake_names


def test_set_compliance_success(mock_chain_fns):
    fake_get, fake_add, fake_names = mock_chain_fns
    set_compliance("mychain", "SOC2", note="Reviewed Q1", get_chain_fn=fake_get, add_chain_fn=fake_add)
    result = get_compliance("mychain", get_chain_fn=fake_get)
    assert "SOC2" in result
    assert result["SOC2"]["note"] == "Reviewed Q1"


def test_set_compliance_invalid_standard(mock_chain_fns):
    fake_get, fake_add, _ = mock_chain_fns
    with pytest.raises(ComplianceError, match="Unknown standard"):
        set_compliance("mychain", "UNKNOWN", get_chain_fn=fake_get, add_chain_fn=fake_add)


def test_set_multiple_standards(mock_chain_fns):
    fake_get, fake_add, _ = mock_chain_fns
    set_compliance("mychain", "HIPAA", get_chain_fn=fake_get, add_chain_fn=fake_add)
    set_compliance("mychain", "GDPR", note="EU reqs", get_chain_fn=fake_get, add_chain_fn=fake_add)
    result = get_compliance("mychain", get_chain_fn=fake_get)
    assert "HIPAA" in result
    assert "GDPR" in result


def test_remove_compliance_success(mock_chain_fns):
    fake_get, fake_add, _ = mock_chain_fns
    set_compliance("mychain", "PCI", get_chain_fn=fake_get, add_chain_fn=fake_add)
    remove_compliance("mychain", "PCI", get_chain_fn=fake_get, add_chain_fn=fake_add)
    result = get_compliance("mychain", get_chain_fn=fake_get)
    assert "PCI" not in result


def test_remove_compliance_not_set_raises(mock_chain_fns):
    fake_get, fake_add, _ = mock_chain_fns
    with pytest.raises(ComplianceError, match="not set"):
        remove_compliance("mychain", "NIST", get_chain_fn=fake_get, add_chain_fn=fake_add)


def test_get_compliance_empty(mock_chain_fns):
    fake_get, _, _ = mock_chain_fns
    result = get_compliance("mychain", get_chain_fn=fake_get)
    assert result == {}


def test_list_by_compliance(mock_chain_fns):
    fake_get, fake_add, fake_names = mock_chain_fns
    fake_add("chain_a", {"X": "1"})
    fake_add("chain_b", {"Y": "2"})
    set_compliance("chain_a", "ISO27001", get_chain_fn=fake_get, add_chain_fn=fake_add)
    set_compliance("chain_b", "SOC2", get_chain_fn=fake_get, add_chain_fn=fake_add)
    result = list_by_compliance("ISO27001", get_chain_names_fn=fake_names, get_chain_fn=fake_get)
    assert "chain_a" in result
    assert "chain_b" not in result


def test_list_by_compliance_no_matches(mock_chain_fns):
    fake_get, _, fake_names = mock_chain_fns
    result = list_by_compliance("GDPR", get_chain_names_fn=fake_names, get_chain_fn=fake_get)
    assert result == []
