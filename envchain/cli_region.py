"""CLI commands for chain region/tier management."""

import click
from envchain.region import (
    set_region,
    get_region,
    clear_region,
    list_by_region,
    RegionError,
    VALID_REGIONS,
)


@click.group("region")
def region_group():
    """Manage environment region/tier tags for chains."""


@region_group.command("set")
@click.argument("chain_name")
@click.argument("region", type=click.Choice(sorted(VALID_REGIONS)))
@click.password_option(prompt="Password")
def region_set(chain_name, region, password):
    """Assign a REGION to CHAIN_NAME."""
    try:
        set_region(chain_name, region, password)
        click.echo(f"Region '{region}' set for chain '{chain_name}'.")
    except RegionError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


@region_group.command("get")
@click.argument("chain_name")
@click.password_option(prompt="Password")
def region_get(chain_name, password):
    """Show the region assigned to CHAIN_NAME."""
    try:
        region = get_region(chain_name, password)
        if region:
            click.echo(region)
        else:
            click.echo(f"No region set for '{chain_name}'.")
    except RegionError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


@region_group.command("clear")
@click.argument("chain_name")
@click.password_option(prompt="Password")
def region_clear(chain_name, password):
    """Remove the region tag from CHAIN_NAME."""
    try:
        clear_region(chain_name, password)
        click.echo(f"Region cleared for chain '{chain_name}'.")
    except RegionError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


@region_group.command("list")
@click.argument("region", type=click.Choice(sorted(VALID_REGIONS)))
@click.password_option(prompt="Password")
def region_list(region, password):
    """List all chains in the given REGION."""
    try:
        chains = list_by_region(region, password)
        if chains:
            for name in chains:
                click.echo(name)
        else:
            click.echo(f"No chains found in region '{region}'.")
    except RegionError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)
