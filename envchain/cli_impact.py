"""CLI commands for managing impact levels of environment chains."""

import click
from envchain.impact import (
    ImpactError,
    set_impact,
    get_impact,
    clear_impact,
    list_by_impact,
)
from envchain.chain import get_chain_names

VALID_LEVELS = ["none", "low", "medium", "high", "critical"]


@click.group(name="impact")
def impact_group():
    """Manage impact levels for environment chains."""


@impact_group.command(name="set")
@click.argument("chain_name")
@click.argument("level", type=click.Choice(VALID_LEVELS, case_sensitive=False))
@click.option("--password", prompt=True, hide_input=True, help="Encryption password.")
def impact_set(chain_name: str, level: str, password: str):
    """Set the impact level for a chain."""
    try:
        set_impact(chain_name, level.lower(), password)
        click.echo(f"Impact level for '{chain_name}' set to '{level.lower()}'.")
    except ImpactError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


@impact_group.command(name="get")
@click.argument("chain_name")
@click.option("--password", prompt=True, hide_input=True, help="Encryption password.")
def impact_get(chain_name: str, password: str):
    """Get the impact level for a chain."""
    try:
        level = get_impact(chain_name, password)
        if level:
            click.echo(f"{chain_name}: {level}")
        else:
            click.echo(f"{chain_name}: (no impact level set)")
    except ImpactError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


@impact_group.command(name="clear")
@click.argument("chain_name")
@click.option("--password", prompt=True, hide_input=True, help="Encryption password.")
def impact_clear(chain_name: str, password: str):
    """Clear the impact level for a chain."""
    try:
        clear_impact(chain_name, password)
        click.echo(f"Impact level cleared for '{chain_name}'.")
    except ImpactError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


@impact_group.command(name="list")
@click.option(
    "--level",
    type=click.Choice(VALID_LEVELS, case_sensitive=False),
    default=None,
    help="Filter by impact level.",
)
@click.option("--password", prompt=True, hide_input=True, help="Encryption password.")
def impact_list(level: str, password: str):
    """List chains grouped by or filtered by impact level."""
    try:
        results = list_by_impact(password, filter_level=level.lower() if level else None)
        if not results:
            click.echo("No chains with impact levels found.")
            return
        for chain_name, chain_level in sorted(results.items(), key=lambda x: VALID_LEVELS.index(x[1])):
            click.echo(f"{chain_name}: {chain_level}")
    except ImpactError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)
