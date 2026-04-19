"""CLI commands for managing chain bookmarks."""

import click
from envchain.bookmark import add_bookmark, remove_bookmark, get_bookmarks, BookmarkError


@click.group("bookmark")
def bookmark_group():
    """Manage bookmarked chains."""


@bookmark_group.command("add")
@click.argument("name")
def bookmark_add(name):
    """Bookmark a chain."""
    try:
        add_bookmark(name)
        click.echo(f"Bookmarked '{name}'.")
    except BookmarkError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


@bookmark_group.command("remove")
@click.argument("name")
def bookmark_remove(name):
    """Remove a bookmark."""
    try:
        remove_bookmark(name)
        click.echo(f"Removed bookmark '{name}'.")
    except BookmarkError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


@bookmark_group.command("list")
def bookmark_list():
    """List all bookmarked chains."""
    bookmarks = get_bookmarks()
    if not bookmarks:
        click.echo("No bookmarks set.")
    else:
        for name in bookmarks:
            click.echo(name)
