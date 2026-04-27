"""CLI commands for chain ownership management."""

import click
from envchain.ownership import (
    OwnershipError,
    set_owner,
    get_owner,
    clear_owner,
    list_by_owner,
)


@click.group("ownership")
def ownership_group():
    """Manage chain ownership."""


@ownership_group.command("set")
@click.argument("chain")
@click.argument("owner")
@click.option("--password", envvar="ENVCHAIN_PASSWORD", prompt=True, hide_input=True)
def ownership_set(chain, owner, password):
    """Assign an owner to a chain."""
    try:
        set_owner(chain, owner, password)
        click.echo(f"Owner of '{chain}' set to '{owner}'.")
    except OwnershipError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


@ownership_group.command("get")
@click.argument("chain")
@click.option("--password", envvar="ENVCHAIN_PASSWORD", prompt=True, hide_input=True)
def ownership_get(chain, password):
    """Show the owner of a chain."""
    try:
        owner = get_owner(chain, password)
        if owner:
            click.echo(owner)
        else:
            click.echo(f"No owner set for '{chain}'.")
    except OwnershipError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


@ownership_group.command("clear")
@click.argument("chain")
@click.option("--password", envvar="ENVCHAIN_PASSWORD", prompt=True, hide_input=True)
def ownership_clear(chain, password):
    """Remove ownership from a chain."""
    try:
        clear_owner(chain, password)
        click.echo(f"Ownership cleared for '{chain}'.")
    except OwnershipError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


@ownership_group.command("list")
@click.argument("owner")
@click.option("--password", envvar="ENVCHAIN_PASSWORD", prompt=True, hide_input=True)
def ownership_list(owner, password):
    """List all chains owned by OWNER."""
    chains = list_by_owner(owner, password)
    if chains:
        for name in chains:
            click.echo(name)
    else:
        click.echo(f"No chains owned by '{owner}'.")
