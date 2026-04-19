"""CLI commands for chain visibility management."""

import click
from envchain.visibility import set_visibility, get_visibility, clear_visibility, list_by_visibility, VisibilityError


@click.group("visibility")
def visibility_group():
    """Manage chain visibility levels."""
    pass


@visibility_group.command("set")
@click.argument("chain")
@click.argument("level", type=click.Choice(["public", "private", "shared"]))
@click.option("--password", prompt=True, hide_input=True)
def visibility_set(chain, level, password):
    """Set visibility level for a chain."""
    try:
        set_visibility(chain, level, password)
        click.echo(f"Visibility of '{chain}' set to '{level}'.")
    except VisibilityError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)
    except KeyError:
        click.echo(f"Error: Chain '{chain}' not found.", err=True)
        raise SystemExit(1)


@visibility_group.command("get")
@click.argument("chain")
@click.option("--password", prompt=True, hide_input=True)
def visibility_get(chain, password):
    """Get visibility level of a chain."""
    try:
        level = get_visibility(chain, password)
        click.echo(level)
    except KeyError:
        click.echo(f"Error: Chain '{chain}' not found.", err=True)
        raise SystemExit(1)


@visibility_group.command("clear")
@click.argument("chain")
@click.option("--password", prompt=True, hide_input=True)
def visibility_clear(chain, password):
    """Clear visibility setting (resets to default 'private')."""
    try:
        clear_visibility(chain, password)
        click.echo(f"Visibility cleared for '{chain}'.")
    except KeyError:
        click.echo(f"Error: Chain '{chain}' not found.", err=True)
        raise SystemExit(1)


@visibility_group.command("list")
@click.argument("level", type=click.Choice(["public", "private", "shared"]))
@click.option("--password", prompt=True, hide_input=True)
def visibility_list(level, password):
    """List all chains with a given visibility level."""
    try:
        chains = list_by_visibility(level, password)
        if not chains:
            click.echo(f"No chains with visibility '{level}'.")
        else:
            for name in chains:
                click.echo(name)
    except VisibilityError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)
