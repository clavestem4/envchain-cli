"""CLI commands for audit log inspection."""

import click
from envchain.audit import read_events, clear_events


@click.group("audit")
def audit_group():
    """View and manage the envchain audit log."""


@audit_group.command("log")
@click.option("--chain", default=None, help="Filter by chain name.")
@click.option("--limit", default=50, show_default=True, help="Max entries to show.")
def audit_log(chain, limit):
    """Display recent audit log entries."""
    events = read_events(chain_name=chain)
    if not events:
        click.echo("No audit events found.")
        return

    for event in events[-limit:]:
        ts = event.get("timestamp", "?")
        action = event.get("action", "?")
        chain_name = event.get("chain", "?")
        detail = event.get("detail", "")
        line = f"[{ts}] {action.upper():8s} {chain_name}"
        if detail:
            line += f"  ({detail})"
        click.echo(line)


@audit_group.command("clear")
@click.option("--chain", default=None, help="Clear only events for this chain.")
@click.confirmation_option(prompt="Are you sure you want to clear audit events?")
def audit_clear(chain):
    """Clear audit log entries."""
    removed = clear_events(chain_name=chain)
    scope = f"chain '{chain}'" if chain else "all chains"
    click.echo(f"Removed {removed} audit event(s) for {scope}.")
