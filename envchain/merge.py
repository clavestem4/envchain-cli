"""Merge variables from one or more chains into a target chain."""

from envchain.chain import get_chain, add_chain, get_chain_names


class MergeError(Exception):
    pass


def merge_chains(
    sources: list[str],
    target: str,
    password: str,
    overwrite_vars: bool = False,
    overwrite_chain: bool = False,
) -> dict:
    """
    Merge variables from multiple source chains into a target chain.

    Returns a dict summarising what was added/skipped.
    """
    chain_names = get_chain_names(password)

    merged_vars: dict[str, str] = {}
    skipped: list[str] = []

    # Load existing target vars if chain already exists
    if target in chain_names:
        if not overwrite_chain:
            existing = get_chain(target, password)
            merged_vars.update(existing)
        # else: start fresh, ignore existing

    added: list[str] = []

    for source in sources:
        if source not in chain_names:
            raise MergeError(f"Source chain '{source}' not found.")
        source_vars = get_chain(source, password)
        for key, value in source_vars.items():
            if key in merged_vars and not overwrite_vars:
                skipped.append(key)
            else:
                if key not in merged_vars or merged_vars[key] != value:
                    added.append(key)
                merged_vars[key] = value

    add_chain(target, merged_vars, password)

    return {
        "target": target,
        "added": added,
        "skipped": skipped,
        "total": len(merged_vars),
    }
