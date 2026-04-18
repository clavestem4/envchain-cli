"""Key rotation: re-encrypt a chain's variables under a new password."""

from envchain.chain import get_chain, add_chain
from envchain.store import load_chain, save_chain


class RotationError(Exception):
    pass


def rotate_chain(chain_name: str, old_password: str, new_password: str) -> dict:
    """Re-encrypt all variables in a chain under a new password.

    Returns the updated chain dict.
    """
    try:
        chain = get_chain(chain_name, old_password)
    except Exception as e:
        raise RotationError(f"Failed to decrypt chain '{chain_name}' with old password: {e}") from e

    try:
        save_chain(chain_name, chain, new_password)
    except Exception as e:
        raise RotationError(f"Failed to re-encrypt chain '{chain_name}': {e}") from e

    return chain


def rotate_all(chain_names: list, old_password: str, new_password: str) -> dict:
    """Rotate multiple chains. Returns a summary dict with success/failure per chain."""
    results = {}
    for name in chain_names:
        try:
            rotate_chain(name, old_password, new_password)
            results[name] = {"status": "ok"}
        except RotationError as e:
            results[name] = {"status": "error", "reason": str(e)}
    return results
