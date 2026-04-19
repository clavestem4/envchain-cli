"""Batch operations on chain groups (export, snapshot, etc.)."""

import click
from envchain.env_group import get_group, GroupError
from envchain.chain import get_chain
from envchain.export import export_chain


@click.group("group-ops")
def group_ops():
    """Batch operations across a chain group."""


@group_ops.command("export")
@click.argument("group_name")
@click.option("--shell", default="bash", type=click.Choice(["bash", "fish", "dotenv"]), show_default=True)
def group_export(group_name, shell):
    """Export all chains in a group."""
    try:
        chains = get_group(group_name)
    except GroupError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)

    for chain_name in chains:
        try:
            output = export_chain(chain_name, shell)
            click.echo(f"# --- {chain_name} ---")
            click.echo(output)
        except Exception as e:
            click.echo(f"Warning: could not export '{chain_name}': {e}", err=True)


@group_ops.command("list-vars")
@click.argument("group_name")
def group_list_vars(group_name):
    """List all variables across chains in a group."""
    try:
        chains = get_group(group_name)
    except GroupError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)

    for chain_name in chains:
        try:
            data = get_chain(chain_name)
            click.echo(f"[{chain_name}]")
            for key in data:
                click.echo(f"  {key}")
        except Exception as e:
            click.echo(f"Warning: could not read '{chain_name}': {e}", err=True)
