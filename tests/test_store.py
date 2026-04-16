"""Tests for envchain.store module."""

import json
import pytest
from pathlib import Path
from envchain.store import ChainStore


@pytest.fixture
def tmp_store(tmp_path):
    return ChainStore(store_path=tmp_path / "store.json")


def test_empty_store_lists_no_chains(tmp_store):
    assert tmp_store.list_chains() == []


def test_set_and_get_var(tmp_store):
    tmp_store.set_var("myproject", "API_KEY", "encrypted_value_abc")
    chain = tmp_store.get_chain("myproject")
    assert chain is not None
    assert chain["API_KEY"] == "encrypted_value_abc"


def test_list_chains_after_set(tmp_store):
    tmp_store.set_var("proj1", "KEY", "val1")
    tmp_store.set_var("proj2", "KEY", "val2")
    assert set(tmp_store.list_chains()) == {"proj1", "proj2"}


def test_delete_var(tmp_store):
    tmp_store.set_var("proj", "KEY", "val")
    result = tmp_store.delete_var("proj", "KEY")
    assert result is True
    assert tmp_store.get_chain("proj") is None  # chain removed when empty


def test_delete_var_nonexistent(tmp_store):
    assert tmp_store.delete_var("ghost", "KEY") is False


def test_delete_chain(tmp_store):
    tmp_store.set_var("proj", "A", "1")
    tmp_store.set_var("proj", "B", "2")
    assert tmp_store.delete_chain("proj") is True
    assert tmp_store.list_chains() == []


def test_persistence(tmp_path):
    path = tmp_path / "store.json"
    s1 = ChainStore(store_path=path)
    s1.set_var("proj", "TOKEN", "enc123")

    s2 = ChainStore(store_path=path)
    assert s2.get_chain("proj")["TOKEN"] == "enc123"


def test_store_file_is_valid_json(tmp_path):
    path = tmp_path / "store.json"
    store = ChainStore(store_path=path)
    store.set_var("p", "K", "V")
    data = json.loads(path.read_text())
    assert data == {"p": {"K": "V"}}
