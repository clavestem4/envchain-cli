"""CLI commands for pinning/favoriting chains."""
import click
from envchain.pin import pin_chain, unpin_chain, get_pinned, is_pinned


@click.group("pin")
def pin_group():
    """Pin chains for quick access."""
    pass


@pin_group.command("add")
@click.argument("name")
def pin_add(name):
    """Pin a chain."""
    try:
        pin_chain(name)
        click.echo(f"Pinned chain '{name}'.")
    except KeyError as e:
        click.echo(str(e), err=True)
        raise SystemExit(1)
    except ValueError as e:
        click.echo(str(e), err=True)
        raise SystemExit(1)


@pin_group.command("remove")
@click.argument("name")
def pin_remove(name):
    """Unpin a chain."""
    try:
        unpin_chain(name)
        click.echo(f"Unpinned chain '{name}'.")
    except KeyError as e:
        click.echo(str(e), err=True)
        raise SystemExit(1)


@pin_group.command("list")
def pin_list():
    """List all pinned chains."""
    pins = get_pinned()
    if not pins:
        click.echo("No pinned chains.")
    else:
        for name in pins:
            click.echo(name)
