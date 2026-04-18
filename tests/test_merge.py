"""Tests for envchain.merge."""

import pytest
from unittest.mock import patch, MagicMock
from envchain.merge import merge_chains, MergeError


PASSWORD = "testpass"


@pytest.fixture
def mock_chain_fns():
    chains = {
        "base": {"HOST": "localhost", "PORT": "5432"},
        "override": {"PORT": "9999", "DEBUG": "true"},
        "extra": {"TOKEN": "abc123"},
    }

    def fake_get(name, pw):
        return dict(chains[name])

    def fake_add(name, vars_, pw):
        chains[name] = dict(vars_)

    def fake_names(pw):
        return list(chains.keys())

    with patch("envchain.merge.get_chain", side_effect=fake_get), \
         patch("envchain.merge.add_chain", side_effect=fake_add), \
         patch("envchain.merge.get_chain_names", side_effect=fake_names):
        yield chains


def test_merge_two_sources_no_conflict(mock_chain_fns):
    result = merge_chains(["base", "extra"], "merged", PASSWORD)
    assert result["target"] == "merged"
    assert "HOST" in result["added"]
    assert "TOKEN" in result["added"]
    assert result["skipped"] == []


def test_merge_conflict_no_overwrite(mock_chain_fns):
    result = merge_chains(["base", "override"], "merged", PASSWORD)
    # PORT from base is set first; override's PORT should be skipped
    assert "PORT" in result["skipped"]
    assert "DEBUG" in result["added"]


def test_merge_conflict_with_overwrite(mock_chain_fns):
    result = merge_chains(["base", "override"], "merged", PASSWORD, overwrite_vars=True)
    assert "PORT" not in result["skipped"]
    assert "DEBUG" in result["added"]


def test_merge_missing_source_raises(mock_chain_fns):
    with pytest.raises(MergeError, match="not found"):
        merge_chains(["nonexistent"], "merged", PASSWORD)


def test_merge_into_existing_chain_preserves_vars(mock_chain_fns):
    # 'base' already exists; merge 'extra' into it without overwrite_chain
    result = merge_chains(["extra"], "base", PASSWORD)
    # HOST and PORT from existing base should be preserved
    assert result["total"] == 3  # HOST, PORT, TOKEN


def test_merge_overwrite_chain_drops_existing(mock_chain_fns):
    result = merge_chains(["extra"], "base", PASSWORD, overwrite_chain=True)
    # Only TOKEN from extra
    assert result["total"] == 1
