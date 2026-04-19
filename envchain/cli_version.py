"""CLI commands for chain version metadata."""

import click
from envchain.version import stamp_chain, get_version_info, list_versioned_chains, VersionError


@click.group("version")
def version_group():
    """Manage chain version metadata."""


@version_group.command("stamp")
@click.argument("chain_name")
@click.option("--password", prompt=True, hide_input=True)
def version_stamp(chain_name, password):
    """Stamp a chain with updated version metadata."""
    try:
        stamp_chain(chain_name, password)
        info = get_version_info(chain_name, password)
        click.echo(f"Stamped '{chain_name}' → version {info['version']}")
    except VersionError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


@version_group.command("info")
@click.argument("chain_name")
@click.option("--password", prompt=True, hide_input=True)
def version_info(chain_name, password):
    """Show version metadata for a chain."""
    try:
        info = get_version_info(chain_name, password)
        if info["version"] is None:
            click.echo(f"Chain '{chain_name}' has no version metadata.")
        else:
            click.echo(f"Chain:      {info['chain']}")
            click.echo(f"Version:    {info['version']}")
            click.echo(f"Created:    {info['created_at']}")
            click.echo(f"Updated:    {info['updated_at']}")
    except VersionError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


@version_group.command("list")
@click.option("--password", prompt=True, hide_input=True)
def version_list(password):
    """List all chains with version metadata."""
    chains = list_versioned_chains(password)
    if not chains:
        click.echo("No versioned chains found.")
    else:
        for name in chains:
            click.echo(name)
