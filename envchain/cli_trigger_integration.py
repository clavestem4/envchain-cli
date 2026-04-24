"""Integration helpers for trigger-aware chain operations."""

import subprocess
from typing import Optional
from envchain.trigger import get_trigger, TriggerError
from envchain.chain import get_chain


def fire_trigger(chain_name: str, event: str) -> Optional[int]:
    """Execute the shell command for the given event on chain_name.

    Returns the process return code, or None if no trigger is set.
    Silently skips execution if no trigger is configured.
    """
    try:
        cmd = get_trigger(chain_name, event)
    except (TriggerError, KeyError):
        return None

    if cmd is None:
        return None

    result = subprocess.run(cmd, shell=True)
    return result.returncode


def get_chain_with_trigger(chain_name: str) -> dict:
    """Retrieve a chain and fire its on_get trigger if set.

    Returns the chain data (excluding internal trigger metadata).
    """
    fire_trigger(chain_name, "on_get")
    chain = get_chain(chain_name)
    return {k: v for k, v in chain.items() if not k.startswith("__")}


def list_trigger_summary(chain_names: list) -> list:
    """Return a summary of trigger coverage across multiple chains.

    Each entry: {"chain": name, "events": [list of configured events]}
    """
    from envchain.trigger import list_triggers
    summary = []
    for name in chain_names:
        try:
            triggers = list_triggers(name)
            summary.append({"chain": name, "events": sorted(triggers.keys())})
        except KeyError:
            continue
    return summary
