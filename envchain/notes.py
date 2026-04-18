"""Per-chain notes/description storage."""
from envchain.chain import get_chain, add_chain

_NOTES_KEY = "__notes__"


def set_note(chain_name: str, note: str, password: str) -> None:
    """Set a note/description for a chain."""
    try:
        chain = get_chain(chain_name, password)
    except KeyError:
        raise KeyError(f"Chain '{chain_name}' not found.")
    chain[_NOTES_KEY] = note
    add_chain(chain_name, chain, password, overwrite=True)


def get_note(chain_name: str, password: str) -> str:
    """Get the note/description for a chain. Returns empty string if none."""
    try:
        chain = get_chain(chain_name, password)
    except KeyError:
        raise KeyError(f"Chain '{chain_name}' not found.")
    return chain.get(_NOTES_KEY, "")


def clear_note(chain_name: str, password: str) -> None:
    """Remove the note from a chain."""
    try:
        chain = get_chain(chain_name, password)
    except KeyError:
        raise KeyError(f"Chain '{chain_name}' not found.")
    chain.pop(_NOTES_KEY, None)
    add_chain(chain_name, chain, password, overwrite=True)
