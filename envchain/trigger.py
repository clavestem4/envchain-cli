"""Trigger module: attach shell command hooks to chain events (on-get, on-set, on-delete)."""

from typing import Optional
from envchain.chain import get_chain, add_chain, get_chain_names

VALID_EVENTS = {"on_get", "on_set", "on_delete"}
_TRIGGER_KEY = "__triggers__"


class TriggerError(Exception):
    pass


def _get_triggers(chain_name: str) -> dict:
    chain = get_chain(chain_name)
    return chain.get(_TRIGGER_KEY, {})


def set_trigger(chain_name: str, event: str, command: str) -> None:
    """Attach a shell command to fire on the given event for chain_name."""
    if event not in VALID_EVENTS:
        raise TriggerError(f"Invalid event '{event}'. Must be one of: {sorted(VALID_EVENTS)}")
    chain = get_chain(chain_name)
    triggers = chain.get(_TRIGGER_KEY, {})
    triggers[event] = command
    chain[_TRIGGER_KEY] = triggers
    add_chain(chain_name, chain, overwrite=True)


def get_trigger(chain_name: str, event: str) -> Optional[str]:
    """Return the command for the given event, or None if not set."""
    if event not in VALID_EVENTS:
        raise TriggerError(f"Invalid event '{event}'. Must be one of: {sorted(VALID_EVENTS)}")
    return _get_triggers(chain_name).get(event)


def remove_trigger(chain_name: str, event: str) -> None:
    """Remove the trigger for the given event from chain_name."""
    if event not in VALID_EVENTS:
        raise TriggerError(f"Invalid event '{event}'. Must be one of: {sorted(VALID_EVENTS)}")
    chain = get_chain(chain_name)
    triggers = chain.get(_TRIGGER_KEY, {})
    if event not in triggers:
        raise TriggerError(f"No trigger set for event '{event}' on chain '{chain_name}'")
    del triggers[event]
    chain[_TRIGGER_KEY] = triggers
    add_chain(chain_name, chain, overwrite=True)


def list_triggers(chain_name: str) -> dict:
    """Return all triggers for chain_name as {event: command}."""
    return dict(_get_triggers(chain_name))


def find_chains_with_trigger(event: str) -> list:
    """Return all chain names that have a trigger for the given event."""
    if event not in VALID_EVENTS:
        raise TriggerError(f"Invalid event '{event}'. Must be one of: {sorted(VALID_EVENTS)}")
    result = []
    for name in get_chain_names():
        triggers = _get_triggers(name)
        if event in triggers:
            result.append(name)
    return result
