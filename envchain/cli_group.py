"""CLI commands for chain group management."""

import click
from envchain.env_group import create_group, get_group, delete_group, list_groups, GroupError


@click.group("group")
def group_cmd():
    """Manage chain groups."""


@group_cmd.command("create")
@click.argument("group_name")
@click.argument("chains", nargs=-1, required=True)
def group_create(group_name, chains):
    """Create a group with the given chains."""
    try:
        create_group(group_name, list(chains))
        click.echo(f"Group '{group_name}' created with chains: {', '.join(chains)}")
    except GroupError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


@group_cmd.command("show")
@click.argument("group_name")
def group_show(group_name):
    """Show chains in a group."""
    try:
        chains = get_group(group_name)
        click.echo(f"Group '{group_name}':")
        for c in chains:
            click.echo(f"  - {c}")
    except GroupError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


@group_cmd.command("delete")
@click.argument("group_name")
def group_delete(group_name):
    """Delete a group."""
    try:
        delete_group(group_name)
        click.echo(f"Group '{group_name}' deleted.")
    except GroupError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


@group_cmd.command("list")
def group_list():
    """List all groups."""
    groups = list_groups()
    if not groups:
        click.echo("No groups defined.")
        return
    for name, chains in groups.items():
        click.echo(f"{name}: {', '.join(chains)}")
