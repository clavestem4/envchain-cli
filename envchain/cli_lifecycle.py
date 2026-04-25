"""CLI commands for managing chain lifecycle states."""

import click
from envchain.lifecycle import (
    VALID_STATES,
    LifecycleError,
    set_lifecycle,
    get_lifecycle,
    clear_lifecycle,
    list_by_lifecycle,
)


@click.group("lifecycle")
def lifecycle_group():
    """Manage lifecycle states for chains."""


@lifecycle_group.command("set")
@click.argument("chain_name")
@click.argument("state", type=click.Choice(sorted(VALID_STATES)))
@click.option("--password", prompt=True, hide_input=True)
def lifecycle_set(chain_name, state, password):
    """Set the lifecycle state of a chain."""
    try:
        set_lifecycle(chain_name, state, password)
        click.echo(f"Lifecycle state for '{chain_name}' set to '{state}'.")
    except LifecycleError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


@lifecycle_group.command("get")
@click.argument("chain_name")
@click.option("--password", prompt=True, hide_input=True)
def lifecycle_get(chain_name, password):
    """Get the lifecycle state of a chain."""
    try:
        state = get_lifecycle(chain_name, password)
        if state:
            click.echo(state)
        else:
            click.echo(f"No lifecycle state set for '{chain_name}'.")
    except LifecycleError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


@lifecycle_group.command("clear")
@click.argument("chain_name")
@click.option("--password", prompt=True, hide_input=True)
def lifecycle_clear(chain_name, password):
    """Clear the lifecycle state of a chain."""
    try:
        clear_lifecycle(chain_name, password)
        click.echo(f"Lifecycle state cleared for '{chain_name}'.")
    except LifecycleError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


@lifecycle_group.command("list")
@click.argument("state", type=click.Choice(sorted(VALID_STATES)))
@click.option("--password", prompt=True, hide_input=True)
def lifecycle_list(state, password):
    """List all chains with a given lifecycle state."""
    try:
        chains = list_by_lifecycle(state, password)
        if chains:
            for name in chains:
                click.echo(name)
        else:
            click.echo(f"No chains with lifecycle state '{state}'.")
    except LifecycleError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)
