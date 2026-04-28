"""CLI commands for managing impact levels on chains."""

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
    """Manage impact levels for chains."""


@impact_group.command(name="set")
@click.argument("chain_name")
@click.argument("level", type=click.Choice(VALID_LEVELS, case_sensitive=False))
@click.option("--reason", "-r", default=None, help="Optional reason for this impact level.")
def impact_set(chain_name: str, level: str, reason: str):
    """Set the impact level for a chain."""
    try:
        set_impact(chain_name, level.lower(), reason=reason)
        click.echo(f"Impact level for '{chain_name}' set to '{level.lower()}'.")
        if reason:
            click.echo(f"Reason: {reason}")
    except ImpactError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


@impact_group.command(name="get")
@click.argument("chain_name")
def impact_get(chain_name: str):
    """Get the impact level for a chain."""
    try:
        info = get_impact(chain_name)
        if info is None:
            click.echo(f"No impact level set for '{chain_name}'.")
        else:
            level = info.get("level", "unknown")
            reason = info.get("reason")
            click.echo(f"Impact: {level}")
            if reason:
                click.echo(f"Reason: {reason}")
    except ImpactError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


@impact_group.command(name="clear")
@click.argument("chain_name")
def impact_clear(chain_name: str):
    """Clear the impact level for a chain."""
    try:
        clear_impact(chain_name)
        click.echo(f"Impact level cleared for '{chain_name}'.")
    except ImpactError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


@impact_group.command(name="list")
@click.option(
    "--level",
    "-l",
    type=click.Choice(VALID_LEVELS, case_sensitive=False),
    default=None,
    help="Filter by impact level.",
)
def impact_list(level: str):
    """List chains grouped by impact level (or filtered by level)."""
    try:
        all_names = get_chain_names()
        if not all_names:
            click.echo("No chains found.")
            return

        if level:
            chains = list_by_impact(level.lower())
            if not chains:
                click.echo(f"No chains with impact level '{level}'.")
            else:
                click.echo(f"Chains with impact '{level}':")
                for name in chains:
                    click.echo(f"  - {name}")
        else:
            # Group all chains by their impact level
            grouped: dict[str, list[str]] = {lvl: [] for lvl in VALID_LEVELS}
            unset = []
            for name in all_names:
                info = get_impact(name)
                if info is None:
                    unset.append(name)
                else:
                    lvl = info.get("level", "none")
                    grouped.setdefault(lvl, []).append(name)

            for lvl in VALID_LEVELS:
                chains_in_level = grouped.get(lvl, [])
                if chains_in_level:
                    click.echo(f"[{lvl}]")
                    for name in chains_in_level:
                        click.echo(f"  - {name}")

            if unset:
                click.echo("[unset]")
                for name in unset:
                    click.echo(f"  - {name}")
    except ImpactError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)
