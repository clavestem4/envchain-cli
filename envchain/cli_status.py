"""CLI commands for chain status management."""

import click
from envchain.status import set_status, get_status, clear_status, list_by_status, StatusError, VALID_STATUSES


@click.group("status")
def status_group():
    """Manage chain status (active, inactive, archived)."""


@status_group.command("set")
@click.argument("chain")
@click.argument("status", type=click.Choice(list(VALID_STATUSES)))
@click.option("--password", prompt=True, hide_input=True)
def status_set(chain, status, password):
    """Set the status of a chain."""
    try:
        set_status(chain, status, password)
        click.echo(f"Status of '{chain}' set to '{status}'.")
    except KeyError:
        click.echo(f"Chain '{chain}' not found.", err=True)
        raise SystemExit(1)
    except StatusError as e:
        click.echo(str(e), err=True)
        raise SystemExit(1)


@status_group.command("get")
@click.argument("chain")
@click.option("--password", prompt=True, hide_input=True)
def status_get(chain, password):
    """Get the status of a chain."""
    try:
        s = get_status(chain, password)
        click.echo(s)
    except KeyError:
        click.echo(f"Chain '{chain}' not found.", err=True)
        raise SystemExit(1)


@status_group.command("clear")
@click.argument("chain")
@click.option("--password", prompt=True, hide_input=True)
def status_clear(chain, password):
    """Clear the status of a chain (resets to active)."""
    try:
        clear_status(chain, password)
        click.echo(f"Status cleared for '{chain}'.")
    except KeyError:
        click.echo(f"Chain '{chain}' not found.", err=True)
        raise SystemExit(1)


@status_group.command("list")
@click.argument("status", type=click.Choice(list(VALID_STATUSES)))
@click.option("--password", prompt=True, hide_input=True)
def status_list(status, password):
    """List chains with a given status."""
    try:
        chains = list_by_status(status, password)
    except StatusError as e:
        click.echo(str(e), err=True)
        raise SystemExit(1)
    if not chains:
        click.echo(f"No chains with status '{status}'.")
    else:
        for name in chains:
            click.echo(name)
