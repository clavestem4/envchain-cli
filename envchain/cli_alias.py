"""CLI commands for chain aliases."""

import click
from envchain.alias import set_alias, remove_alias, resolve_alias, list_aliases


@click.group("alias")
def alias_group():
    """Manage chain aliases."""


@alias_group.command("set")
@click.argument("alias")
@click.argument("target")
def alias_set(alias, target):
    """Create or update ALIAS pointing to TARGET chain."""
    try:
        set_alias(alias, target)
        click.echo(f"Alias '{alias}' -> '{target}' set.")
    except KeyError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


@alias_group.command("remove")
@click.argument("alias")
def alias_remove(alias):
    """Remove an alias."""
    try:
        remove_alias(alias)
        click.echo(f"Alias '{alias}' removed.")
    except KeyError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


@alias_group.command("resolve")
@click.argument("alias")
def alias_resolve(alias):
    """Print the chain name that ALIAS resolves to."""
    target = resolve_alias(alias)
    click.echo(target)


@alias_group.command("list")
def alias_list():
    """List all aliases."""
    aliases = list_aliases()
    if not aliases:
        click.echo("No aliases defined.")
        return
    for alias, target in sorted(aliases.items()):
        click.echo(f"{alias} -> {target}")
