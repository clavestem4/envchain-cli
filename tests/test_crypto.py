"""Tests for envchain.crypto module."""

import pytest
from envchain.crypto import encrypt, decrypt


PASSWORD = "super-secret-password"
PLAINTEXT = "MY_SECRET=hello_world"


def test_encrypt_returns_string():
    token = encrypt(PLAINTEXT, PASSWORD)
    assert isinstance(token, str)
    assert len(token) > 0


def test_encrypt_different_each_time():
    token1 = encrypt(PLAINTEXT, PASSWORD)
    token2 = encrypt(PLAINTEXT, PASSWORD)
    assert token1 != token2  # random salt/nonce


def test_decrypt_roundtrip():
    token = encrypt(PLAINTEXT, PASSWORD)
    result = decrypt(token, PASSWORD)
    assert result == PLAINTEXT


def test_decrypt_wrong_password():
    token = encrypt(PLAINTEXT, PASSWORD)
    with pytest.raises(ValueError, match="Decryption failed"):
        decrypt(token, "wrong-password")


def test_decrypt_invalid_token():
    with pytest.raises(ValueError):
        decrypt("not-a-valid-token!!", PASSWORD)


def test_decrypt_truncated_token():
    with pytest.raises(ValueError):
        decrypt("YWJj", PASSWORD)  # too short after decode


def test_encrypt_empty_string():
    token = encrypt("", PASSWORD)
    assert decrypt(token, PASSWORD) == ""


def test_encrypt_unicode():
    text = "VAR=héllo wörld 🔑"
    token = encrypt(text, PASSWORD)
    assert decrypt(token, PASSWORD) == text
