"""Tests for envchain.tags module."""
import pytest
from unittest.mock import patch, MagicMock

from envchain.tags import add_tag, remove_tag, get_tags, find_by_tag, TAGS_KEY

PASSWORD = "test-pass"


@pytest.fixture
def mock_chain_fns():
    store = {}

    def fake_get_chain(name, pw):
        if name not in store:
            raise KeyError(name)
        return dict(store[name])

    def fake_add_chain(name, chain, pw, overwrite=False):
        store[name] = dict(chain)

    def fake_get_chain_names(pw):
        return list(store.keys())

    with patch("envchain.tags.get_chain", side_effect=fake_get_chain), \
         patch("envchain.tags.add_chain", side_effect=fake_add_chain), \
         patch("envchain.tags.get_chain_names", side_effect=fake_get_chain_names):
        store["mychain"] = {"API_KEY": "secret"}
        yield store


def test_add_tag(mock_chain_fns):
    add_tag("mychain", "production", PASSWORD)
    assert "production" in mock_chain_fns["mychain"][TAGS_KEY]


def test_add_tag_no_duplicates(mock_chain_fns):
    add_tag("mychain", "production", PASSWORD)
    add_tag("mychain", "production", PASSWORD)
    tags_raw = mock_chain_fns["mychain"][TAGS_KEY]
    assert tags_raw.count("production") == 1


def test_remove_tag(mock_chain_fns):
    mock_chain_fns["mychain"][TAGS_KEY] = "production,staging"
    remove_tag("mychain", "production", PASSWORD)
    tags_raw = mock_chain_fns["mychain"][TAGS_KEY]
    assert "production" not in tags_raw
    assert "staging" in tags_raw


def test_get_tags_empty(mock_chain_fns):
    tags = get_tags("mychain", PASSWORD)
    assert tags == []


def test_get_tags_multiple(mock_chain_fns):
    mock_chain_fns["mychain"][TAGS_KEY] = "a,b,c"
    tags = get_tags("mychain", PASSWORD)
    assert tags == ["a", "b", "c"]


def test_find_by_tag(mock_chain_fns):
    mock_chain_fns["mychain"][TAGS_KEY] = "production"
    mock_chain_fns["other"] = {"X": "1", TAGS_KEY: "staging"}
    results = find_by_tag("production", PASSWORD)
    assert "mychain" in results
    assert "other" not in results


def test_find_by_tag_no_match(mock_chain_fns):
    results = find_by_tag("nonexistent", PASSWORD)
    assert results == []
