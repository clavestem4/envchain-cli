"""Import/export chains to/from portable encrypted JSON bundles."""

import json
import base64
from pathlib import Path
from typing import Optional

from envchain.crypto import encrypt, decrypt
from envchain.chain import get_chain, add_chain


def export_bundle(chain_name: str, password: str, store_path: Optional[Path] = None) -> str:
    """Export a chain as an encrypted JSON bundle string."""
    env_vars = get_chain(chain_name, password, store_path=store_path)
    plaintext = json.dumps({"chain": chain_name, "vars": env_vars})
    token = encrypt(plaintext, password)
    bundle = {"version": 1, "chain": chain_name, "data": token}
    return json.dumps(bundle)


def import_bundle(
    bundle_str: str,
    password: str,
    chain_name: Optional[str] = None,
    overwrite: bool = False,
    store_path: Optional[Path] = None,
) -> str:
    """Import a chain from an encrypted JSON bundle string.

    Returns the chain name that was imported.
    Raises ValueError if chain exists and overwrite=False.
    """
    try:
        bundle = json.loads(bundle_str)
    except json.JSONDecodeError as exc:
        raise ValueError("Invalid bundle format: not valid JSON") from exc

    if bundle.get("version") != 1:
        raise ValueError("Unsupported bundle version")

    plaintext = decrypt(bundle["data"], password)
    payload = json.loads(plaintext)

    target_name = chain_name or payload["chain"]
    env_vars = payload["vars"]

    from envchain.chain import get_chain_names
    existing = get_chain_names(store_path=store_path)
    if target_name in existing and not overwrite:
        raise ValueError(
            f"Chain '{target_name}' already exists. Use overwrite=True to replace it."
        )

    add_chain(target_name, env_vars, password, store_path=store_path)
    return target_name


def export_bundle_to_file(chain_name: str, password: str, filepath: Path, store_path: Optional[Path] = None) -> None:
    """Write an encrypted bundle to a file."""
    bundle_str = export_bundle(chain_name, password, store_path=store_path)
    filepath.write_text(bundle_str, encoding="utf-8")


def import_bundle_from_file(
    filepath: Path,
    password: str,
    chain_name: Optional[str] = None,
    overwrite: bool = False,
    store_path: Optional[Path] = None,
) -> str:
    """Read an encrypted bundle from a file and import it."""
    bundle_str = filepath.read_text(encoding="utf-8")
    return import_bundle(bundle_str, password, chain_name=chain_name, overwrite=overwrite, store_path=store_path)
