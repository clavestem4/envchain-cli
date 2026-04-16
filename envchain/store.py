"""Persistent storage for encrypted envchain chains."""

import json
from pathlib import Path
from typing import Dict, Optional

DEFAULT_STORE_PATH = Path.home() / ".envchain" / "store.json"


class ChainStore:
    """JSON-backed store for encrypted environment variable chains."""

    def __init__(self, store_path: Path = DEFAULT_STORE_PATH) -> None:
        self.store_path = store_path
        self._data: Dict[str, Dict[str, str]] = {}
        self._load()

    def _load(self) -> None:
        if self.store_path.exists():
            with self.store_path.open("r", encoding="utf-8") as fh:
                self._data = json.load(fh)
        else:
            self._data = {}

    def _save(self) -> None:
        self.store_path.parent.mkdir(parents=True, exist_ok=True)
        with self.store_path.open("w", encoding="utf-8") as fh:
            json.dump(self._data, fh, indent=2)

    def list_chains(self):
        return list(self._data.keys())

    def get_chain(self, chain: str) -> Optional[Dict[str, str]]:
        return self._data.get(chain)

    def set_var(self, chain: str, key: str, encrypted_value: str) -> None:
        self._data.setdefault(chain, {})[key] = encrypted_value
        self._save()

    def delete_var(self, chain: str, key: str) -> bool:
        if chain in self._data and key in self._data[chain]:
            del self._data[chain][key]
            if not self._data[chain]:
                del self._data[chain]
            self._save()
            return True
        return False

    def delete_chain(self, chain: str) -> bool:
        if chain in self._data:
            del self._data[chain]
            self._save()
            return True
        return False
