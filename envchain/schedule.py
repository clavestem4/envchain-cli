"""Schedule-based auto-refresh hints for chains."""
from datetime import datetime, timedelta
from typing import Optional
from envchain.chain import get_chain, add_chain

SCHEDULE_KEY = "__schedule__"

SUPPORTED_INTERVALS = {
    "hourly": timedelta(hours=1),
    "daily": timedelta(days=1),
    "weekly": timedelta(weeks=1),
}


def set_schedule(chain_name: str, interval: str, password: str) -> None:
    """Attach a refresh schedule to a chain."""
    if interval not in SUPPORTED_INTERVALS:
        raise ValueError(f"Unsupported interval '{interval}'. Choose from: {list(SUPPORTED_INTERVALS)}.")
    chain = get_chain(chain_name, password)
    chain[SCHEDULE_KEY] = interval
    add_chain(chain_name, chain, password, overwrite=True)


def get_schedule(chain_name: str, password: str) -> Optional[str]:
    """Return the schedule interval for a chain, or None."""
    chain = get_chain(chain_name, password)
    return chain.get(SCHEDULE_KEY)


def clear_schedule(chain_name: str, password: str) -> None:
    """Remove the schedule from a chain."""
    chain = get_chain(chain_name, password)
    if SCHEDULE_KEY in chain:
        del chain[SCHEDULE_KEY]
        add_chain(chain_name, chain, password, overwrite=True)


def is_due(chain_name: str, password: str, last_run: datetime) -> bool:
    """Return True if the chain is due for a refresh based on its schedule."""
    interval_name = get_schedule(chain_name, password)
    if not interval_name:
        return False
    delta = SUPPORTED_INTERVALS[interval_name]
    return datetime.utcnow() >= last_run + delta


def list_scheduled(chain_names: list, password: str) -> list:
    """Return list of (chain_name, interval) tuples for chains that have a schedule."""
    result = []
    for name in chain_names:
        try:
            interval = get_schedule(name, password)
            if interval:
                result.append((name, interval))
        except Exception:
            continue
    return result
