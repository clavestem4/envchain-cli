"""Tests for envchain/annotation.py"""

import pytest
from unittest.mock import patch, MagicMock
from envchain.annotation import (
    set_annotation,
    remove_annotation,
    get_annotations,
    find_by_annotation,
    AnnotationError,
    ANNOTATION_KEY,
)


@pytest.fixture
def mock_chain_fns():
    store = {}

    def fake_get(name, password):
        if name not in store:
            raise KeyError(name)
        return dict(store[name])

    def fake_add(name, chain, password, overwrite=False):
        store[name] = dict(chain)

    def fake_names(password):
        return list(store.keys())

    with patch("envchain.annotation.get_chain", side_effect=fake_get), \
         patch("envchain.annotation.add_chain", side_effect=fake_add):
        store["mychain"] = {"FOO": "bar"}
        yield store, fake_names


def test_set_annotation_creates_entry(mock_chain_fns):
    store, _ = mock_chain_fns
    set_annotation("mychain", "owner", "alice", "secret")
    assert ANNOTATION_KEY in store["mychain"]
    assert "owner=alice" in store["mychain"][ANNOTATION_KEY]


def test_set_multiple_annotations(mock_chain_fns):
    store, _ = mock_chain_fns
    set_annotation("mychain", "owner", "alice", "secret")
    set_annotation("mychain", "team", "platform", "secret")
    annotations = get_annotations("mychain", "secret")
    assert annotations["owner"] == "alice"
    assert annotations["team"] == "platform"


def test_remove_annotation(mock_chain_fns):
    store, _ = mock_chain_fns
    set_annotation("mychain", "owner", "alice", "secret")
    remove_annotation("mychain", "owner", "secret")
    annotations = get_annotations("mychain", "secret")
    assert "owner" not in annotations


def test_remove_missing_annotation_raises(mock_chain_fns):
    _, _ = mock_chain_fns
    with pytest.raises(AnnotationError, match="not found"):
        remove_annotation("mychain", "nonexistent", "secret")


def test_get_annotations_empty(mock_chain_fns):
    _, _ = mock_chain_fns
    result = get_annotations("mychain", "secret")
    assert result == {}


def test_find_by_annotation_key_only(mock_chain_fns):
    store, fake_names = mock_chain_fns
    store["chain_a"] = {ANNOTATION_KEY: "env=prod"}
    store["chain_b"] = {ANNOTATION_KEY: "env=staging"}
    store["chain_c"] = {"VAR": "value"}
    results = find_by_annotation("env", None, fake_names, "secret")
    assert "chain_a" in results
    assert "chain_b" in results
    assert "chain_c" not in results


def test_find_by_annotation_key_and_value(mock_chain_fns):
    store, fake_names = mock_chain_fns
    store["chain_a"] = {ANNOTATION_KEY: "env=prod"}
    store["chain_b"] = {ANNOTATION_KEY: "env=staging"}
    results = find_by_annotation("env", "prod", fake_names, "secret")
    assert results == ["chain_a"]


def test_find_by_annotation_no_match(mock_chain_fns):
    _, fake_names = mock_chain_fns
    results = find_by_annotation("nonexistent", None, fake_names, "secret")
    assert results == []
