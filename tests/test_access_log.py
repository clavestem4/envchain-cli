import pytest
from pathlib import Path
from envchain.access_log import record_access, get_access_log, clear_access_log, list_accessed_chains


@pytest.fixture
def log_dir(tmp_path):
    return tmp_path / "access_logs"


def test_record_access_creates_file(log_dir):
    record_access("mychain", "get", user="alice", base_dir=log_dir)
    log_file = log_dir / "mychain.jsonl"
    assert log_file.exists()


def test_record_access_entry_structure(log_dir):
    record_access("mychain", "get", user="alice", base_dir=log_dir)
    entries = get_access_log("mychain", base_dir=log_dir)
    assert len(entries) == 1
    e = entries[0]
    assert e["chain"] == "mychain"
    assert e["action"] == "get"
    assert e["user"] == "alice"
    assert "timestamp" in e


def test_record_multiple_entries(log_dir):
    record_access("mychain", "get", user="alice", base_dir=log_dir)
    record_access("mychain", "export", user="bob", base_dir=log_dir)
    entries = get_access_log("mychain", base_dir=log_dir)
    assert len(entries) == 2


def test_get_access_log_filter_by_action(log_dir):
    record_access("mychain", "get", user="alice", base_dir=log_dir)
    record_access("mychain", "export", user="bob", base_dir=log_dir)
    record_access("mychain", "get", user="carol", base_dir=log_dir)
    entries = get_access_log("mychain", action="get", base_dir=log_dir)
    assert len(entries) == 2
    assert all(e["action"] == "get" for e in entries)


def test_get_access_log_missing_chain(log_dir):
    entries = get_access_log("nonexistent", base_dir=log_dir)
    assert entries == []


def test_clear_access_log(log_dir):
    record_access("mychain", "get", user="alice", base_dir=log_dir)
    clear_access_log("mychain", base_dir=log_dir)
    assert get_access_log("mychain", base_dir=log_dir) == []


def test_clear_access_log_nonexistent(log_dir):
    # Should not raise
    clear_access_log("ghost", base_dir=log_dir)


def test_list_accessed_chains(log_dir):
    record_access("alpha", "get", base_dir=log_dir)
    record_access("beta", "export", base_dir=log_dir)
    chains = list_accessed_chains(base_dir=log_dir)
    assert "alpha" in chains
    assert "beta" in chains


def test_list_accessed_chains_empty(log_dir):
    result = list_accessed_chains(base_dir=log_dir)
    assert result == []
