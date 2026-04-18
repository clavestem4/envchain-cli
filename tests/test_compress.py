"""Tests for envchain.compress."""

import pytest
from unittest.mock import patch, MagicMock
from envchain.compress import compress_chain, decompress_chain, compressed_size, CompressError


FAKE_VARS = {"API_KEY": "secret", "DEBUG": "true"}


@pytest.fixture
def mock_chain_fns():
    with patch("envchain.compress.get_chain") as mock_get, \
         patch("envchain.compress.add_chain") as mock_add:
        mock_get.return_value = FAKE_VARS
        yield mock_get, mock_add


def test_compress_returns_string(mock_chain_fns):
    mock_get, _ = mock_chain_fns
    blob = compress_chain("mychain", "pass")
    assert isinstance(blob, str)
    assert len(blob) > 0


def test_compress_decompress_roundtrip(mock_chain_fns):
    mock_get, mock_add = mock_chain_fns
    mock_get.side_effect = [FAKE_VARS, Exception("not found")]
    blob = compress_chain("mychain", "pass")
    mock_get.side_effect = Exception("not found")
    name = decompress_chain(blob, "pass")
    assert name == "mychain"
    mock_add.assert_called_once_with("mychain", FAKE_VARS, "pass")


def test_decompress_with_rename(mock_chain_fns):
    mock_get, mock_add = mock_chain_fns
    blob = compress_chain("mychain", "pass")
    mock_get.side_effect = Exception("not found")
    name = decompress_chain(blob, "pass", new_name="renamed")
    assert name == "renamed"
    mock_add.assert_called_once_with("renamed", FAKE_VARS, "pass")


def test_decompress_raises_if_exists_no_overwrite(mock_chain_fns):
    mock_get, mock_add = mock_chain_fns
    blob = compress_chain("mychain", "pass")
    mock_get.side_effect = [FAKE_VARS, FAKE_VARS]
    with pytest.raises(CompressError, match="already exists"):
        decompress_chain(blob, "pass", overwrite=False)


def test_decompress_overwrite_allowed(mock_chain_fns):
    mock_get, mock_add = mock_chain_fns
    blob = compress_chain("mychain", "pass")
    mock_get.side_effect = [FAKE_VARS, FAKE_VARS]
    name = decompress_chain(blob, "pass", overwrite=True)
    assert name == "mychain"


def test_decompress_invalid_blob():
    with pytest.raises(CompressError, match="Failed to decompress"):
        decompress_chain("notvalidbase64!!!", "pass")


def test_compressed_size(mock_chain_fns):
    blob = compress_chain("mychain", "pass")
    size = compressed_size(blob)
    assert isinstance(size, int)
    assert size > 0
