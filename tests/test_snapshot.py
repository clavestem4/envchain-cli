"""Tests for envchain/snapshot.py"""

import pytest
import os
from envchain.snapshot import save_snapshot, load_snapshot, list_snapshots, delete_snapshot


@pytest.fixture(autouse=True)
def tmp_snapshot_dir(tmp_path, monkeypatch):
    monkeypatch.setattr("envchain.snapshot.SNAPSHOT_DIR", str(tmp_path / "snapshots"))
    yield


VARS = {"KEY": "value", "FOO": "bar"}


def test_save_and_load_snapshot():
    name = save_snapshot("mychain", VARS, "snap1")
    assert name == "snap1"
    loaded = load_snapshot("mychain", "snap1")
    assert loaded == VARS


def test_save_snapshot_auto_name():
    name = save_snapshot("mychain", VARS)
    assert name  # not empty
    loaded = load_snapshot("mychain", name)
    assert loaded == VARS


def test_list_snapshots_empty():
    assert list_snapshots("nochain") == []


def test_list_snapshots_multiple():
    save_snapshot("mychain", VARS, "b_snap")
    save_snapshot("mychain", VARS, "a_snap")
    names = list_snapshots("mychain")
    assert names == ["a_snap", "b_snap"]


def test_load_missing_snapshot_raises():
    with pytest.raises(FileNotFoundError):
        load_snapshot("mychain", "ghost")


def test_delete_snapshot():
    save_snapshot("mychain", VARS, "to_delete")
    delete_snapshot("mychain", "to_delete")
    assert "to_delete" not in list_snapshots("mychain")


def test_delete_missing_snapshot_raises():
    with pytest.raises(FileNotFoundError):
        delete_snapshot("mychain", "nope")


def test_snapshots_isolated_by_chain():
    save_snapshot("chainA", VARS, "snap1")
    save_snapshot("chainB", {"X": "1"}, "snap1")
    assert load_snapshot("chainA", "snap1") == VARS
    assert load_snapshot("chainB", "snap1") == {"X": "1"}
