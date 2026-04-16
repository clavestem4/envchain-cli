"""Persistent storage for encrypted envchain chains."""

import json
import os
from pathlib import Path
from typing import Dict, Optional

DEFAULT_STORE_PATH = Path.home() / ".envchain" / "store.json"


def _load_store(store_path: Path) -> Dict:
    if not store_path.exists():
        return {}
    with store_path.open("r") as f:
        return json.load(f)


def _save_store(data: Dict, store_path: Path) -> None:
    store_path.parent.mkdir(parents=True, exist_ok=True)
    with store_path.open("w") as f:
        json.dump(data, f, indent=2)
    os.chmod(store_path, 0o600)


def save_chain(chain_name: str, encrypted_vars: Dict[str, str], store_path: Path = DEFAULT_STORE_PATH) -> None:
    """Save an encrypted variable chain to the store."""
    data = _load_store(store_path)
    data[chain_name] = encrypted_vars
    _save_store(data, store_path)


def load_chain(chain_name: str, store_path: Path = DEFAULT_STORE_PATH) -> Optional[Dict[str, str]]:
    """Load an encrypted variable chain from the store."""
    data = _load_store(store_path)
    return data.get(chain_name)


def list_chains(store_path: Path = DEFAULT_STORE_PATH):
    """Return all chain names in the store."""
    return list(_load_store(store_path).keys())


def delete_chain(chain_name: str, store_path: Path = DEFAULT_STORE_PATH) -> bool:
    """Delete a chain from the store. Returns True if deleted."""
    data = _load_store(store_path)
    if chain_name not in data:
        return False
    del data[chain_name]
    _save_store(data, store_path)
    return True
