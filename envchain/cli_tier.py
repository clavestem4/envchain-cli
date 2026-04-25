"""CLI commands for tier management."""

import click
from envchain.tier import (
    set_tier,
    get_tier,
    clear_tier,
    list_by_tier,
    VALID_TIERS,
    TierError,
)


@click.group("tier")
def tier_group():
    """Manage tier assignments for chains."""


@tier_group.command("set")
@click.argument("chain_name")
@click.argument("tier", type=click.Choice(sorted(VALID_TIERS)))
@click.password_option("--password", prompt="Password")
def tier_set(chain_name, tier, password):
    """Assign a tier to a chain."""
    try:
        set_tier(chain_name, tier, password)
        click.echo(f"Tier '{tier}' set for chain '{chain_name}'.")
    except TierError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


@tier_group.command("get")
@click.argument("chain_name")
@click.password_option("--password", prompt="Password")
def tier_get(chain_name, password):
    """Get the tier assigned to a chain."""
    try:
        tier = get_tier(chain_name, password)
        if tier:
            click.echo(tier)
        else:
            click.echo(f"No tier set for chain '{chain_name}'.")
    except TierError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


@tier_group.command("clear")
@click.argument("chain_name")
@click.password_option("--password", prompt="Password")
def tier_clear(chain_name, password):
    """Remove the tier assignment from a chain."""
    try:
        clear_tier(chain_name, password)
        click.echo(f"Tier cleared for chain '{chain_name}'.")
    except TierError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


@tier_group.command("list")
@click.argument("tier", type=click.Choice(sorted(VALID_TIERS)))
@click.password_option("--password", prompt="Password")
def tier_list(tier, password):
    """List all chains assigned to a given tier."""
    try:
        chains = list_by_tier(tier, password)
        if chains:
            for name in chains:
                click.echo(name)
        else:
            click.echo(f"No chains assigned to tier '{tier}'.")
    except TierError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)
