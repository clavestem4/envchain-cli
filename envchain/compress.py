"""Chain compression: gzip + base64 encode/decode for compact storage or sharing."""

import gzip
import base64
import json
from envchain.chain import get_chain, add_chain


class CompressError(Exception):
    pass


def compress_chain(chain_name: str, password: str) -> str:
    """Export a chain as a compressed, base64-encoded string."""
    data = get_chain(chain_name, password)
    payload = json.dumps({"name": chain_name, "vars": data}).encode("utf-8")
    compressed = gzip.compress(payload)
    return base64.urlsafe_b64encode(compressed).decode("ascii")


def decompress_chain(blob: str, password: str, new_name: str = None, overwrite: bool = False) -> str:
    """Import a chain from a compressed blob. Returns the chain name used."""
    try:
        compressed = base64.urlsafe_b64decode(blob.encode("ascii"))
        payload = gzip.decompress(compressed)
        data = json.loads(payload.decode("utf-8"))
    except CompressError:
        raise
    except gzip.BadGzipFile as e:
        raise CompressError(f"Blob is not valid gzip data: {e}") from e
    except (ValueError, KeyError) as e:
        raise CompressError(f"Blob contains invalid JSON structure: {e}") from e
    except Exception as e:
        raise CompressError(f"Failed to decompress blob: {e}") from e

    chain_name = new_name or data.get("name")
    if not chain_name:
        raise CompressError("Blob is missing required 'name' field and no new_name provided.")

    vars_ = data.get("vars")
    if vars_ is None:
        raise CompressError("Blob is missing required 'vars' field.")

    try:
        existing = get_chain(chain_name, password)
        if existing and not overwrite:
            raise CompressError(f"Chain '{chain_name}' already exists. Use overwrite=True to replace.")
    except CompressError:
        raise
    except Exception:
        pass

    add_chain(chain_name, vars_, password)
    return chain_name


def compressed_size(blob: str) -> int:
    """Return byte size of the compressed blob."""
    return len(base64.urlsafe_b64decode(blob.encode("ascii")))
