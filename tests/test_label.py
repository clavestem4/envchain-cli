"""Tests for envchain.label module."""

import pytest
from unittest.mock import patch, MagicMock
from envchain.label import set_label, remove_label, get_labels, find_by_label, LabelError

PASSWORD = "test"


@pytest.fixture
def mock_chain_fns():
    store = {}

    def fake_get(name, pw):
        if name not in store:
            raise KeyError(f"Chain '{name}' not found.")
        return dict(store[name])

    def fake_add(name, data, pw, overwrite=False):
        store[name] = dict(data)

    def fake_names(pw):
        return list(store.keys())

    with patch("envchain.label.get_chain", side_effect=fake_get), \
         patch("envchain.label.add_chain", side_effect=fake_add), \
         patch("envchain.label.get_chain_names", side_effect=fake_names):
        store["mychain"] = {"FOO": "bar"}
        yield store


def test_set_label(mock_chain_fns):
    set_label("mychain", "env", "production", PASSWORD)
    labels = get_labels("mychain", PASSWORD)
    assert labels["env"] == "production"


def test_set_multiple_labels(mock_chain_fns):
    set_label("mychain", "env", "staging", PASSWORD)
    set_label("mychain", "team", "backend", PASSWORD)
    labels = get_labels("mychain", PASSWORD)
    assert labels["env"] == "staging"
    assert labels["team"] == "backend"


def test_remove_label(mock_chain_fns):
    set_label("mychain", "env", "dev", PASSWORD)
    remove_label("mychain", "env", PASSWORD)
    labels = get_labels("mychain", PASSWORD)
    assert "env" not in labels


def test_remove_missing_label_raises(mock_chain_fns):
    with pytest.raises(LabelError):
        remove_label("mychain", "nonexistent", PASSWORD)


def test_get_labels_empty(mock_chain_fns):
    labels = get_labels("mychain", PASSWORD)
    assert labels == {}


def test_find_by_label(mock_chain_fns):
    mock_chain_fns["chain2"] = {"X": "1"}
    set_label("mychain", "env", "prod", PASSWORD)
    set_label("chain2", "env", "dev", PASSWORD)
    results = find_by_label("env", "prod", PASSWORD)
    assert "mychain" in results
    assert "chain2" not in results


def test_find_by_label_no_match(mock_chain_fns):
    results = find_by_label("env", "prod", PASSWORD)
    assert results == []
