"""Tests for envchain.checkpoint module."""

import pytest
from unittest.mock import patch, call
from envchain.checkpoint import (
    save_checkpoint,
    restore_checkpoint,
    list_checkpoints,
    delete_checkpoint,
    CheckpointError,
    _CHECKPOINT_KEY,
)


@pytest.fixture()
def mock_chain_fns():
    store = {}

    def fake_get(name, password):
        if name not in store:
            raise KeyError(name)
        return dict(store[name])

    def fake_add(name, data, password, overwrite=False):
        store[name] = dict(data)

    with patch("envchain.checkpoint.get_chain", side_effect=fake_get), \
         patch("envchain.checkpoint.add_chain", side_effect=fake_add):
        yield store


def test_save_checkpoint_creates_entry(mock_chain_fns):
    mock_chain_fns["mychain"] = {"FOO": "bar", "BAZ": "qux"}
    info = save_checkpoint("mychain", "v1", "secret")
    assert "saved_at" in info
    assert info["vars"] == {"FOO": "bar", "BAZ": "qux"}
    assert _CHECKPOINT_KEY in mock_chain_fns["mychain"]
    assert "v1" in mock_chain_fns["mychain"][_CHECKPOINT_KEY]


def test_save_checkpoint_excludes_meta_keys(mock_chain_fns):
    mock_chain_fns["mychain"] = {"FOO": "bar", "__meta__": "skip"}
    info = save_checkpoint("mychain", "v1", "secret")
    assert "__meta__" not in info["vars"]
    assert "FOO" in info["vars"]


def test_list_checkpoints_empty(mock_chain_fns):
    mock_chain_fns["mychain"] = {"FOO": "bar"}
    result = list_checkpoints("mychain", "secret")
    assert result == {}


def test_list_checkpoints_after_save(mock_chain_fns):
    mock_chain_fns["mychain"] = {"FOO": "bar"}
    save_checkpoint("mychain", "alpha", "secret")
    save_checkpoint("mychain", "beta", "secret")
    result = list_checkpoints("mychain", "secret")
    assert set(result.keys()) == {"alpha", "beta"}


def test_restore_checkpoint_replaces_vars(mock_chain_fns):
    mock_chain_fns["mychain"] = {"FOO": "original"}
    save_checkpoint("mychain", "snap", "secret")
    # Mutate chain after checkpoint
    mock_chain_fns["mychain"]["FOO"] = "changed"
    mock_chain_fns["mychain"]["NEW"] = "extra"
    restored = restore_checkpoint("mychain", "snap", "secret")
    assert restored["FOO"] == "original"
    assert "NEW" not in restored
    assert mock_chain_fns["mychain"]["FOO"] == "original"


def test_restore_checkpoint_missing_label(mock_chain_fns):
    mock_chain_fns["mychain"] = {"FOO": "bar"}
    with pytest.raises(CheckpointError, match="not found"):
        restore_checkpoint("mychain", "nonexistent", "secret")


def test_delete_checkpoint_removes_entry(mock_chain_fns):
    mock_chain_fns["mychain"] = {"FOO": "bar"}
    save_checkpoint("mychain", "v1", "secret")
    delete_checkpoint("mychain", "v1", "secret")
    result = list_checkpoints("mychain", "secret")
    assert "v1" not in result


def test_delete_checkpoint_missing_raises(mock_chain_fns):
    mock_chain_fns["mychain"] = {"FOO": "bar"}
    with pytest.raises(CheckpointError, match="not found"):
        delete_checkpoint("mychain", "ghost", "secret")
