"""CLI commands for viewing and managing chain change history."""

import click
from envchain.history import get_history, clear_history


@click.group(name="history")
def history_group():
    """View and manage chain change history."""
    pass


@history_group.command(name="log")
@click.argument("chain", required=False)
@click.option("--action", default=None, help="Filter by action (add/update/delete/remove_chain).")
@click.option("--limit", default=20, show_default=True, help="Max number of entries to show.")
def history_log(chain, action, limit):
    """Show history log, optionally filtered by CHAIN and/or action."""
    events = get_history(chain=chain, action=action)
    if not events:
        click.echo("No history found.")
        return
    for event in events[-limit:]:
        variable_part = f" [{event['variable']}]" if event.get("variable") else ""
        note_part = f" — {event['note']}" if event.get("note") else ""
        click.echo(
            f"{event['timestamp']}  {event['chain']}  {event['action']}{variable_part}{note_part}"
        )


@history_group.command(name="clear")
@click.argument("chain", required=False)
@click.option("--yes", is_flag=True, help="Skip confirmation prompt.")
def history_clear(chain, yes):
    """Clear history for CHAIN or all history if no chain specified."""
    target = f"chain '{chain}'" if chain else "ALL chains"
    if not yes:
        click.confirm(f"Clear history for {target}?", abort=True)
    removed = clear_history(chain=chain)
    click.echo(f"Removed {removed} history event(s).")
