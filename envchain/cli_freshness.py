import click
from envchain.freshness import (
    set_freshness,
    get_freshness,
    clear_freshness,
    is_stale,
    list_stale,
    FreshnessError,
)
from envchain.chain import get_chain, add_chain, get_chain_names


@click.group("freshness")
def freshness_group():
    """Manage freshness policies for chains."""


@freshness_group.command("set")
@click.argument("chain_name")
@click.argument("max_age")
def freshness_set(chain_name, max_age):
    """Set max age for CHAIN_NAME (e.g. '7 days', '12 hours')."""
    try:
        set_freshness(chain_name, max_age, get_chain, add_chain)
        click.echo(f"Freshness policy set for '{chain_name}': {max_age}")
    except FreshnessError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


@freshness_group.command("get")
@click.argument("chain_name")
def freshness_get(chain_name):
    """Show freshness policy for CHAIN_NAME."""
    try:
        meta = get_freshness(chain_name, get_chain)
        if not meta:
            click.echo(f"No freshness policy set for '{chain_name}'.")
        else:
            click.echo(f"max_age: {meta['max_age']}")
            click.echo(f"updated_at: {meta.get('updated_at', 'unknown')}")
            stale = is_stale(chain_name, get_chain)
            click.echo(f"stale: {stale}")
    except FreshnessError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


@freshness_group.command("clear")
@click.argument("chain_name")
def freshness_clear(chain_name):
    """Remove freshness policy from CHAIN_NAME."""
    try:
        clear_freshness(chain_name, get_chain, add_chain)
        click.echo(f"Freshness policy cleared for '{chain_name}'.")
    except FreshnessError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


@freshness_group.command("stale")
def freshness_stale():
    """List all chains whose freshness policy has expired."""
    stale_chains = list_stale(get_chain_names, get_chain)
    if not stale_chains:
        click.echo("No stale chains found.")
    else:
        for name in stale_chains:
            click.echo(name)
