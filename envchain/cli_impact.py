"""CLI commands for managing chain impact levels."""

import click
from envchain.impact import (
    ImpactError,
    VALID_LEVELS,
    set_impact,
    get_impact,
    clear_impact,
    list_by_impact,
)


@click.group("impact")
def impact_group():
    """Manage impact levels for chains."""


@impact_group.command("set")
@click.argument("chain_name")
@click.argument("level", type=click.Choice(VALID_LEVELS, case_sensitive=False))
@click.password_option("--password", "-p", prompt="Password")
def impact_set(chain_name: str, level: str, password: str):
    """Set the impact level for a chain."""
    try:
        set_impact(chain_name, level, password)
        click.echo(f"Impact level for '{chain_name}' set to '{level}'.")
    except ImpactError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)
    except KeyError:
        click.echo(f"Error: Chain '{chain_name}' not found.", err=True)
        raise SystemExit(1)


@impact_group.command("get")
@click.argument("chain_name")
@click.password_option("--password", "-p", prompt="Password")
def impact_get(chain_name: str, password: str):
    """Get the impact level for a chain."""
    try:
        level = get_impact(chain_name, password)
        if level:
            click.echo(level)
        else:
            click.echo(f"No impact level set for '{chain_name}'.")
    except KeyError:
        click.echo(f"Error: Chain '{chain_name}' not found.", err=True)
        raise SystemExit(1)


@impact_group.command("clear")
@click.argument("chain_name")
@click.password_option("--password", "-p", prompt="Password")
def impact_clear(chain_name: str, password: str):
    """Clear the impact level for a chain."""
    try:
        clear_impact(chain_name, password)
        click.echo(f"Impact level cleared for '{chain_name}'.")
    except KeyError:
        click.echo(f"Error: Chain '{chain_name}' not found.", err=True)
        raise SystemExit(1)


@impact_group.command("list")
@click.argument("level", type=click.Choice(VALID_LEVELS, case_sensitive=False))
@click.password_option("--password", "-p", prompt="Password")
def impact_list(level: str, password: str):
    """List all chains with the given impact level."""
    try:
        chains = list_by_impact(level, password)
        if chains:
            for name in chains:
                click.echo(name)
        else:
            click.echo(f"No chains with impact level '{level}'.")
    except ImpactError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)
