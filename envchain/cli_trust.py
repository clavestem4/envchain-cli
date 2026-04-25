"""CLI commands for trust level management."""

import click
from envchain.trust import (
    set_trust,
    get_trust,
    clear_trust,
    list_by_trust,
    TRUST_LEVELS,
    TrustError,
)


@click.group("trust")
def trust_group():
    """Manage trust levels for chains."""
    pass


@trust_group.command("set")
@click.argument("chain_name")
@click.argument("level", type=click.Choice(TRUST_LEVELS))
@click.option("--password", envvar="ENVCHAIN_PASSWORD", prompt=True, hide_input=True)
def trust_set(chain_name, level, password):
    """Set the trust level for a chain."""
    try:
        set_trust(chain_name, level, password)
        click.echo(f"Trust level for '{chain_name}' set to '{level}'.")
    except (TrustError, KeyError) as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


@trust_group.command("get")
@click.argument("chain_name")
@click.option("--password", envvar="ENVCHAIN_PASSWORD", prompt=True, hide_input=True)
def trust_get(chain_name, password):
    """Get the trust level of a chain."""
    try:
        level = get_trust(chain_name, password)
        if level:
            click.echo(level)
        else:
            click.echo(f"No trust level set for '{chain_name}'.")
    except KeyError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


@trust_group.command("clear")
@click.argument("chain_name")
@click.option("--password", envvar="ENVCHAIN_PASSWORD", prompt=True, hide_input=True)
def trust_clear(chain_name, password):
    """Clear the trust level from a chain."""
    try:
        clear_trust(chain_name, password)
        click.echo(f"Trust level cleared for '{chain_name}'.")
    except KeyError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


@trust_group.command("list")
@click.argument("level", type=click.Choice(TRUST_LEVELS))
@click.option("--password", envvar="ENVCHAIN_PASSWORD", prompt=True, hide_input=True)
def trust_list(level, password):
    """List all chains with a given trust level."""
    try:
        chains = list_by_trust(level, password)
        if chains:
            for name in chains:
                click.echo(name)
        else:
            click.echo(f"No chains with trust level '{level}'.")
    except TrustError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)
