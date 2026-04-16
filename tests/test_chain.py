"""Tests for envchain.chain module."""

import pytest
import tempfile
from pathlib import Path
from envchain.chain import add_chain, get_chain, remove_chain, get_chain_names


@pytest.fixture
def tmp_store(tmp_path):
    return tmp_path / "store.json"


def test_add_and_get_chain(tmp_store):
    variables = {"DB_HOST": "localhost", "DB_PASS": "secret"}
    add_chain("myproject", variables, "master-pass", store_path=tmp_store)
    result = get_chain("myproject", "master-pass", store_path=tmp_store)
    assert result == variables


def test_get_missing_chain_raises(tmp_store):
    with pytest.raises(KeyError, match="not found"):
        get_chain("nonexistent", "pass", store_path=tmp_store)


def test_list_chains(tmp_store):
    add_chain("alpha", {"A": "1"}, "pass", store_path=tmp_store)
    add_chain("beta", {"B": "2"}, "pass", store_path=tmp_store)
    names = get_chain_names(store_path=tmp_store)
    assert set(names) == {"alpha", "beta"}


def test_remove_chain(tmp_store):
    add_chain("temp", {"X": "y"}, "pass", store_path=tmp_store)
    removed = remove_chain("temp", store_path=tmp_store)
    assert removed is True
    assert "temp" not in get_chain_names(store_path=tmp_store)


def test_remove_nonexistent_chain(tmp_store):
    result = remove_chain("ghost", store_path=tmp_store)
    assert result is False


def test_wrong_password_on_get(tmp_store):
    add_chain("proj", {"KEY": "val"}, "correct", store_path=tmp_store)
    with pytest.raises(Exception):
        get_chain("proj", "wrong", store_path=tmp_store)
