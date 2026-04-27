"""Tests for envchain.lineage."""

import pytest
from unittest.mock import patch, MagicMock
from envchain.lineage import (
    set_parent,
    get_parent,
    clear_parent,
    get_children,
    get_ancestors,
    LineageError,
)

PASSWORD = "test-pass"


@pytest.fixture()
def mock_chain_fns():
    store: dict[str, dict] = {}

    def fake_get(name, pw):
        if name not in store:
            raise KeyError(name)
        return dict(store[name])

    def fake_add(name, data, pw, overwrite=False):
        store[name] = dict(data)

    def fake_names(pw):
        return list(store.keys())

    with patch("envchain.lineage.get_chain", side_effect=fake_get), \
         patch("envchain.lineage.add_chain", side_effect=fake_add), \
         patch("envchain.lineage.get_chain_names", side_effect=fake_names):
        store["alpha"] = {"VAR": "1"}
        store["beta"] = {"VAR": "2"}
        store["gamma"] = {"VAR": "3"}
        yield store


def test_set_and_get_parent(mock_chain_fns):
    set_parent("beta", "alpha", PASSWORD)
    assert get_parent("beta", PASSWORD) == "alpha"


def test_get_parent_unset(mock_chain_fns):
    assert get_parent("alpha", PASSWORD) is None


def test_set_parent_missing_chain(mock_chain_fns):
    with pytest.raises(LineageError, match="'missing' not found"):
        set_parent("missing", "alpha", PASSWORD)


def test_set_parent_missing_parent(mock_chain_fns):
    with pytest.raises(LineageError, match="Parent chain 'ghost' not found"):
        set_parent("beta", "ghost", PASSWORD)


def test_set_parent_self_reference(mock_chain_fns):
    with pytest.raises(LineageError, match="cannot be its own parent"):
        set_parent("alpha", "alpha", PASSWORD)


def test_clear_parent(mock_chain_fns):
    set_parent("beta", "alpha", PASSWORD)
    clear_parent("beta", PASSWORD)
    assert get_parent("beta", PASSWORD) is None


def test_get_children(mock_chain_fns):
    set_parent("beta", "alpha", PASSWORD)
    set_parent("gamma", "alpha", PASSWORD)
    children = get_children("alpha", PASSWORD)
    assert children == ["beta", "gamma"]


def test_get_children_none(mock_chain_fns):
    assert get_children("alpha", PASSWORD) == []


def test_get_ancestors_chain(mock_chain_fns):
    set_parent("beta", "alpha", PASSWORD)
    set_parent("gamma", "beta", PASSWORD)
    ancestors = get_ancestors("gamma", PASSWORD)
    assert ancestors == ["beta", "alpha"]


def test_get_ancestors_no_parent(mock_chain_fns):
    assert get_ancestors("alpha", PASSWORD) == []


def test_get_ancestors_stops_on_cycle(mock_chain_fns):
    # Manually inject a cycle to ensure no infinite loop
    mock_chain_fns["alpha"]["__lineage__"] = {"parent": "beta"}
    mock_chain_fns["beta"]["__lineage__"] = {"parent": "alpha"}
    ancestors = get_ancestors("alpha", PASSWORD)
    assert len(ancestors) <= 2
