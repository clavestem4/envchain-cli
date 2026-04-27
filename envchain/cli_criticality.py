"""CLI commands for managing chain criticality levels."""

import click
from envchain.criticality import (
    set_criticality,
    get_criticality,
    clear_criticality,
    list_by_criticality,
    VALID_LEVELS,
    CriticalityError,
)


@click.group("criticality")
def criticality_group():
    """Manage criticality levels for chains."""


@criticality_group.command("set")
@click.argument("chain_name")
@click.argument("level", type=click.Choice(VALID_LEVELS, case_sensitive=False))
@click.password_option("--password", prompt="Password")
def criticality_set(chain_name, level, password):
    """Set the criticality level of a chain."""
    try:
        set_criticality(chain_name, level, password)
        click.echo(f"Criticality for '{chain_name}' set to '{level}'.")
    except CriticalityError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)
    except KeyError:
        click.echo(f"Error: Chain '{chain_name}' not found.", err=True)
        raise SystemExit(1)


@criticality_group.command("get")
@click.argument("chain_name")
@click.password_option("--password", prompt="Password")
def criticality_get(chain_name, password):
    """Get the criticality level of a chain."""
    try:
        level = get_criticality(chain_name, password)
        if level:
            click.echo(level)
        else:
            click.echo(f"No criticality set for '{chain_name}'.")
    except KeyError:
        click.echo(f"Error: Chain '{chain_name}' not found.", err=True)
        raise SystemExit(1)


@criticality_group.command("clear")
@click.argument("chain_name")
@click.password_option("--password", prompt="Password")
def criticality_clear(chain_name, password):
    """Clear the criticality level of a chain."""
    try:
        clear_criticality(chain_name, password)
        click.echo(f"Criticality cleared for '{chain_name}'.")
    except KeyError:
        click.echo(f"Error: Chain '{chain_name}' not found.", err=True)
        raise SystemExit(1)


@criticality_group.command("list")
@click.argument("level", type=click.Choice(VALID_LEVELS, case_sensitive=False))
@click.password_option("--password", prompt="Password")
def criticality_list(level, password):
    """List all chains with a given criticality level."""
    try:
        chains = list_by_criticality(level, password)
        if chains:
            for name in chains:
                click.echo(name)
        else:
            click.echo(f"No chains with criticality '{level}'.")
    except CriticalityError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)
