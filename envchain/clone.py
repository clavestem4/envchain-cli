"""Clone/copy chains within the store."""

from envchain.chain import get_chain, add_chain, get_chain_names


def clone_chain(chain_name: str, new_name: str, password: str, overwrite: bool = False) -> dict:
    """Clone an existing chain to a new name.

    Args:
        chain_name: Source chain name.
        new_name: Destination chain name.
        password: Encryption password.
        overwrite: If True, overwrite existing destination chain.

    Returns:
        The cloned chain data.

    Raises:
        KeyError: If source chain does not exist.
        ValueError: If destination already exists and overwrite is False.
    """
    existing_names = get_chain_names(password)

    if chain_name not in existing_names:
        raise KeyError(f"Chain '{chain_name}' does not exist.")

    if new_name in existing_names and not overwrite:
        raise ValueError(
            f"Chain '{new_name}' already exists. Use overwrite=True to replace it."
        )

    source = get_chain(chain_name, password)
    cloned = dict(source)
    add_chain(new_name, cloned, password)
    return cloned


def rename_chain(chain_name: str, new_name: str, password: str) -> dict:
    """Rename a chain by cloning then removing the original.

    Args:
        chain_name: Existing chain name.
        new_name: New chain name.
        password: Encryption password.

    Returns:
        The renamed chain data.

    Raises:
        KeyError: If source chain does not exist.
        ValueError: If destination already exists.
    """
    from envchain.chain import remove_chain

    cloned = clone_chain(chain_name, new_name, password, overwrite=False)
    remove_chain(chain_name, password)
    return cloned
