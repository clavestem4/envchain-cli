"""High-level chain management: encrypt/decrypt env var sets."""

from typing import Dict
from envchain.crypto import encrypt, decrypt
from envchain.store import save_chain, load_chain, list_chains, delete_chain
from pathlib import Path


def add_chain(chain_name: str, variables: Dict[str, str], password: str, store_path=None) -> None:
    """Encrypt and persist a named set of environment variables."""
    kwargs = {"store_path": store_path} if store_path else {}
    encrypted = {key: encrypt(value, password) for key, value in variables.items()}
    save_chain(chain_name, encrypted, **kwargs)


def get_chain(chain_name: str, password: str, store_path=None) -> Dict[str, str]:
    """Load and decrypt a named set of environment variables."""
    kwargs = {"store_path": store_path} if store_path else {}
    encrypted = load_chain(chain_name, **kwargs)
    if encrypted is None:
        raise KeyError(f"Chain '{chain_name}' not found.")
    return {key: decrypt(value, password) for key, value in encrypted.items()}


def remove_chain(chain_name: str, store_path=None) -> bool:
    """Remove a chain from the store."""
    kwargs = {"store_path": store_path} if store_path else {}
    return delete_chain(chain_name, **kwargs)


def get_chain_names(store_path=None):
    """List all stored chain names."""
    kwargs = {"store_path": store_path} if store_path else {}
    return list_chains(**kwargs)
