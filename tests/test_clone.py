"""Tests for envchain.clone module."""

import pytest
from unittest.mock import patch, MagicMock

from envchain.clone import clone_chain, rename_chain

EXISTING_NAMES = ["prod", "staging"]
PROD_CHAIN = {"DB_URL": "postgres://prod", "SECRET": "abc123"}


@pytest.fixture
def mock_chain_fns():
    with patch("envchain.clone.get_chain_names", return_value=list(EXISTING_NAMES)) as mock_names, \
         patch("envchain.clone.get_chain", return_value=dict(PROD_CHAIN)) as mock_get, \
         patch("envchain.clone.add_chain") as mock_add:
        yield mock_names, mock_get, mock_add


def test_clone_chain_success(mock_chain_fns):
    _, mock_get, mock_add = mock_chain_fns
    result = clone_chain("prod", "prod-backup", "pass")
    mock_get.assert_called_once_with("prod", "pass")
    mock_add.assert_called_once_with("prod-backup", PROD_CHAIN, "pass")
    assert result == PROD_CHAIN


def test_clone_chain_source_missing(mock_chain_fns):
    with pytest.raises(KeyError, match="does not exist"):
        clone_chain("nonexistent", "copy", "pass")


def test_clone_chain_dest_exists_no_overwrite(mock_chain_fns):
    with pytest.raises(ValueError, match="already exists"):
        clone_chain("prod", "staging", "pass")


def test_clone_chain_dest_exists_with_overwrite(mock_chain_fns):
    _, mock_get, mock_add = mock_chain_fns
    result = clone_chain("prod", "staging", "pass", overwrite=True)
    mock_add.assert_called_once_with("staging", PROD_CHAIN, "pass")
    assert result == PROD_CHAIN


def test_rename_chain_success(mock_chain_fns):
    _, mock_get, mock_add = mock_chain_fns
    with patch("envchain.clone.remove_chain") as mock_remove:
        result = rename_chain("prod", "prod-new", "pass")
        mock_add.assert_called_once_with("prod-new", PROD_CHAIN, "pass")
        mock_remove.assert_called_once_with("prod", "pass")
        assert result == PROD_CHAIN


def test_rename_chain_dest_exists_raises(mock_chain_fns):
    with pytest.raises(ValueError, match="already exists"):
        rename_chain("prod", "staging", "pass")


def test_clone_preserves_all_vars(mock_chain_fns):
    _, mock_get, mock_add = mock_chain_fns
    clone_chain("prod", "prod-copy", "pass")
    called_data = mock_add.call_args[0][1]
    assert called_data == PROD_CHAIN
