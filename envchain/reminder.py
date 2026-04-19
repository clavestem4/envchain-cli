"""Reminder module: attach due-date reminders to chains."""
from datetime import datetime
from envchain.chain import get_chain, add_chain, get_chain_names

REMINDER_KEY = "__reminder__"
DATE_FMT = "%Y-%m-%d"


class ReminderError(Exception):
    pass


def set_reminder(chain_name: str, date_str: str, note: str = "", password: str = "") -> None:
    try:
        datetime.strptime(date_str, DATE_FMT)
    except ValueError:
        raise ReminderError(f"Invalid date format: '{date_str}'. Expected YYYY-MM-DD.")
    chain = get_chain(chain_name, password)
    chain[REMINDER_KEY] = f"{date_str}|{note}"
    add_chain(chain_name, chain, password, overwrite=True)


def get_reminder(chain_name: str, password: str = "") -> dict | None:
    chain = get_chain(chain_name, password)
    raw = chain.get(REMINDER_KEY)
    if not raw:
        return None
    parts = raw.split("|", 1)
    return {"date": parts[0], "note": parts[1] if len(parts) > 1 else ""}


def clear_reminder(chain_name: str, password: str = "") -> None:
    chain = get_chain(chain_name, password)
    if REMINDER_KEY in chain:
        del chain[REMINDER_KEY]
        add_chain(chain_name, chain, password, overwrite=True)


def list_due_reminders(password: str = "") -> list[dict]:
    today = datetime.today().date()
    due = []
    for name in get_chain_names():
        try:
            reminder = get_reminder(name, password)
        except Exception:
            continue
        if reminder:
            due_date = datetime.strptime(reminder["date"], DATE_FMT).date()
            if due_date <= today:
                due.append({"chain": name, "date": reminder["date"], "note": reminder["note"]})
    return due
