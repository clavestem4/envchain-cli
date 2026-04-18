"""Tests for envchain.rotate."""

import pytest
from unittest.mock import patch, MagicMock
from envchain.rotate import rotate_chain, rotate_all, RotationError


FAKE_CHAIN = {"API_KEY": "secret", "TOKEN": "abc123"}


@patch("envchain.rotate.save_chain")
@patch("envchain.rotate.get_chain", return_value=FAKE_CHAIN)
def test_rotate_chain_success(mock_get, mock_save):
    result = rotate_chain("myproject", "oldpass", "newpass")
    mock_get.assert_called_once_with("myproject", "oldpass")
    mock_save.assert_called_once_with("myproject", FAKE_CHAIN, "newpass")
    assert result == FAKE_CHAIN


@patch("envchain.rotate.get_chain", side_effect=Exception("bad password"))
def test_rotate_chain_wrong_old_password(mock_get):
    with pytest.raises(RotationError, match="old password"):
        rotate_chain("myproject", "wrongpass", "newpass")


@patch("envchain.rotate.save_chain", side_effect=Exception("disk error"))
@patch("envchain.rotate.get_chain", return_value=FAKE_CHAIN)
def test_rotate_chain_save_failure(mock_get, mock_save):
    with pytest.raises(RotationError, match="re-encrypt"):
        rotate_chain("myproject", "oldpass", "newpass")


@patch("envchain.rotate.save_chain")
@patch("envchain.rotate.get_chain", return_value=FAKE_CHAIN)
def test_rotate_all_success(mock_get, mock_save):
    results = rotate_all(["proj1", "proj2"], "oldpass", "newpass")
    assert results["proj1"]["status"] == "ok"
    assert results["proj2"]["status"] == "ok"
    assert mock_get.call_count == 2


@patch("envchain.rotate.save_chain")
@patch("envchain.rotate.get_chain", side_effect=[FAKE_CHAIN, Exception("fail")])
def test_rotate_all_partial_failure(mock_get, mock_save):
    results = rotate_all(["proj1", "proj2"], "oldpass", "newpass")
    assert results["proj1"]["status"] == "ok"
    assert results["proj2"]["status"] == "error"
    assert "fail" in results["proj2"]["reason"]


@patch("envchain.rotate.save_chain")
@patch("envchain.rotate.get_chain", return_value=FAKE_CHAIN)
def test_rotate_all_empty(mock_get, mock_save):
    results = rotate_all([], "oldpass", "newpass")
    assert results == {}
