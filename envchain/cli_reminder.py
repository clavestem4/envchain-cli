"""CLI commands for chain reminders."""
import click
from envchain.reminder import set_reminder, get_reminder, clear_reminder, list_due_reminders, ReminderError


@click.group("reminder")
def reminder_group():
    """Manage due-date reminders for chains."""


@reminder_group.command("set")
@click.argument("chain_name")
@click.argument("date")
@click.option("--note", default="", help="Optional reminder note.")
@click.option("--password", default="", envvar="ENVCHAIN_PASSWORD")
def reminder_set(chain_name, date, note, password):
    """Set a reminder for CHAIN_NAME due on DATE (YYYY-MM-DD)."""
    try:
        set_reminder(chain_name, date, note, password)
        click.echo(f"Reminder set for '{chain_name}' on {date}.")
    except ReminderError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)
    except KeyError:
        click.echo(f"Error: chain '{chain_name}' not found.", err=True)
        raise SystemExit(1)


@reminder_group.command("get")
@click.argument("chain_name")
@click.option("--password", default="", envvar="ENVCHAIN_PASSWORD")
def reminder_get(chain_name, password):
    """Show the reminder for CHAIN_NAME."""
    try:
        reminder = get_reminder(chain_name, password)
    except KeyError:
        click.echo(f"Error: chain '{chain_name}' not found.", err=True)
        raise SystemExit(1)
    if reminder:
        note_part = f" — {reminder['note']}" if reminder["note"] else ""
        click.echo(f"{reminder['date']}{note_part}")
    else:
        click.echo("No reminder set.")


@reminder_group.command("clear")
@click.argument("chain_name")
@click.option("--password", default="", envvar="ENVCHAIN_PASSWORD")
def reminder_clear(chain_name, password):
    """Clear the reminder for CHAIN_NAME."""
    try:
        clear_reminder(chain_name, password)
        click.echo(f"Reminder cleared for '{chain_name}'.")
    except KeyError:
        click.echo(f"Error: chain '{chain_name}' not found.", err=True)
        raise SystemExit(1)


@reminder_group.command("due")
@click.option("--password", default="", envvar="ENVCHAIN_PASSWORD")
def reminder_due(password):
    """List all chains with reminders due today or earlier."""
    items = list_due_reminders(password)
    if not items:
        click.echo("No reminders due.")
    else:
        for item in items:
            note_part = f" — {item['note']}" if item["note"] else ""
            click.echo(f"{item['chain']}: {item['date']}{note_part}")
