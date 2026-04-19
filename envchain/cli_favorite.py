"""CLI commands for managing favorite chains."""

import click
from envchain.favorite import add_favorite, remove_favorite, get_favorites, is_favorite, FavoriteError


@click.group("favorite")
def favorite_group():
    """Manage favorite chains."""


@favorite_group.command("add")
@click.argument("name")
@click.option("--password", prompt=True, hide_input=True)
def favorite_add(name, password):
    """Mark a chain as a favorite."""
    try:
        add_favorite(name, password)
        click.echo(f"Chain '{name}' added to favorites.")
    except FavoriteError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


@favorite_group.command("remove")
@click.argument("name")
@click.option("--password", prompt=True, hide_input=True)
def favorite_remove(name, password):
    """Remove a chain from favorites."""
    try:
        remove_favorite(name, password)
        click.echo(f"Chain '{name}' removed from favorites.")
    except FavoriteError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


@favorite_group.command("list")
def favorite_list():
    """List all favorite chains."""
    favs = get_favorites()
    if not favs:
        click.echo("No favorites set.")
    else:
        for name in favs:
            click.echo(name)


@favorite_group.command("check")
@click.argument("name")
def favorite_check(name):
    """Check if a chain is a favorite."""
    if is_favorite(name):
        click.echo(f"'{name}' is a favorite.")
    else:
        click.echo(f"'{name}' is not a favorite.")
