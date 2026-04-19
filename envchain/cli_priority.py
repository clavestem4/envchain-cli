"""CLI commands for chain priority management."""

import click
from envchain.priority import set_priority, get_priority, clear_priority, list_by_priority, PriorityError


@click.group("priority")
def priority_group():
    """Manage chain priorities."""


@priority_group.command("set")
@click.argument("chain")
@click.argument("value", type=int)
@click.option("--password", prompt=True, hide_input=True)
def priority_set(chain, value, password):
    """Set priority for a chain."""
    try:
        set_priority(chain, value, password)
        click.echo(f"Priority for '{chain}' set to {value}.")
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


@priority_group.command("get")
@click.argument("chain")
@click.option("--password", prompt=True, hide_input=True)
def priority_get(chain, password):
    """Get priority of a chain."""
    try:
        p = get_priority(chain, password)
        if p is None:
            click.echo(f"'{chain}' has no priority set.")
        else:
            click.echo(f"{p}")
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


@priority_group.command("clear")
@click.argument("chain")
@click.option("--password", prompt=True, hide_input=True)
def priority_clear(chain, password):
    """Clear priority from a chain."""
    try:
        clear_priority(chain, password)
        click.echo(f"Priority cleared for '{chain}'.")
    except PriorityError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


@priority_group.command("list")
@click.option("--password", prompt=True, hide_input=True)
def priority_list(password):
    """List chains sorted by priority."""
    try:
        items = list_by_priority(password)
        if not items:
            click.echo("No chains found.")
            return
        for name, p in items:
            label = str(p) if p is not None else "(unset)"
            click.echo(f"{name}: {label}")
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)
