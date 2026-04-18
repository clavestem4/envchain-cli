"""Tests for envchain.crypto module."""

import pytest
from cryptography.exceptions import InvalidTag
from envchain.crypto import encrypt, decrypt


def test_encrypt_returns_string():
    token = encrypt("hello", "password123")
    assert isinstance(token, str)
    assert len(token) > 0


def test_decrypt_roundtrip():
    plaintext = "SECRET_VALUE"
    password = "my-secure-password"
    token = encrypt(plaintext, password)
    result = decrypt(token, password)
    assert result == plaintext


def test_encrypt_different_tokens_same_input():
    """Each encryption should produce a unique token (random salt/nonce)."""
    t1 = encrypt("value", "pass")
    t2 = encrypt("value", "pass")
    assert t1 != t2


def test_decrypt_wrong_password_raises():
    token = encrypt("secret", "correct-password")
    with pytest.raises(InvalidTag):
        decrypt(token, "wrong-password")


def test_encrypt_empty_string():
    token = encrypt("", "password")
    assert decrypt(token, "password") == ""


def test_encrypt_unicode():
    plaintext = "пароль=секрет"
    token = encrypt(plaintext, "pass")
    assert decrypt(token, "pass") == plaintext


def test_decrypt_tampered_token_raises():
    """Modifying the token after encryption should cause decryption to fail."""
    import base64

    token = encrypt("sensitive", "password")
    raw = bytearray(base64.urlsafe_b64decode(token + "=="))
    raw[-1] ^= 0xFF  # flip bits in the last byte (ciphertext/tag area)
    tampered = base64.urlsafe_b64encode(bytes(raw)).rstrip(b"=").decode()
    with pytest.raises(InvalidTag):
        decrypt(tampered, "password")
