"""Checkpoint module: mark chains with named restore points and roll back to them."""

from datetime import datetime, timezone
from envchain.chain import get_chain, add_chain, get_chain_names


class CheckpointError(Exception):
    pass


_CHECKPOINT_KEY = "__checkpoints__"


def _get_checkpoints(chain: dict) -> dict:
    return chain.get(_CHECKPOINT_KEY, {})


def save_checkpoint(chain_name: str, label: str, password: str) -> dict:
    """Save current state of a chain as a named checkpoint."""
    chain = get_chain(chain_name, password)
    checkpoints = _get_checkpoints(chain)
    snapshot = {k: v for k, v in chain.items() if not k.startswith("__")}
    checkpoints[label] = {
        "vars": snapshot,
        "saved_at": datetime.now(timezone.utc).isoformat(),
    }
    chain[_CHECKPOINT_KEY] = checkpoints
    add_chain(chain_name, chain, password, overwrite=True)
    return checkpoints[label]


def restore_checkpoint(chain_name: str, label: str, password: str) -> dict:
    """Restore a chain's variables to a previously saved checkpoint."""
    chain = get_chain(chain_name, password)
    checkpoints = _get_checkpoints(chain)
    if label not in checkpoints:
        raise CheckpointError(f"Checkpoint '{label}' not found on chain '{chain_name}'.")
    restored_vars = checkpoints[label]["vars"]
    new_chain = {k: v for k, v in chain.items() if k.startswith("__")}
    new_chain.update(restored_vars)
    new_chain[_CHECKPOINT_KEY] = checkpoints
    add_chain(chain_name, new_chain, password, overwrite=True)
    return restored_vars


def list_checkpoints(chain_name: str, password: str) -> dict:
    """Return all checkpoints for a chain, keyed by label."""
    chain = get_chain(chain_name, password)
    return _get_checkpoints(chain)


def delete_checkpoint(chain_name: str, label: str, password: str) -> None:
    """Remove a named checkpoint from a chain."""
    chain = get_chain(chain_name, password)
    checkpoints = _get_checkpoints(chain)
    if label not in checkpoints:
        raise CheckpointError(f"Checkpoint '{label}' not found on chain '{chain_name}'.")
    del checkpoints[label]
    chain[_CHECKPOINT_KEY] = checkpoints
    add_chain(chain_name, chain, password, overwrite=True)
