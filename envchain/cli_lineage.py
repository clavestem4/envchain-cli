"""CLI commands for chain lineage management."""

import click
from envchain.lineage import (
    set_parent,
    get_parent,
    clear_parent,
    get_children,
    get_ancestors,
    LineageError,
)


@click.group("lineage")
def lineage_group():
    """Manage parent/child relationships between chains."""


@lineage_group.command("set-parent")
@click.argument("chain")
@click.argument("parent")
@click.password_option(prompt="Password", confirmation_prompt=False)
def lineage_set_parent(chain, parent, password):
    """Set PARENT as the parent of CHAIN."""
    try:
        set_parent(chain, parent, password)
        click.echo(f"Set '{parent}' as parent of '{chain}'.")
    except LineageError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


@lineage_group.command("get-parent")
@click.argument("chain")
@click.password_option(prompt="Password", confirmation_prompt=False)
def lineage_get_parent(chain, password):
    """Show the parent of CHAIN."""
    try:
        parent = get_parent(chain, password)
        if parent:
            click.echo(parent)
        else:
            click.echo(f"No parent set for '{chain}'.")
    except LineageError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


@lineage_group.command("clear-parent")
@click.argument("chain")
@click.password_option(prompt="Password", confirmation_prompt=False)
def lineage_clear_parent(chain, password):
    """Remove the parent declaration from CHAIN."""
    try:
        clear_parent(chain, password)
        click.echo(f"Parent cleared for '{chain}'.")
    except LineageError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


@lineage_group.command("children")
@click.argument("chain")
@click.password_option(prompt="Password", confirmation_prompt=False)
def lineage_children(chain, password):
    """List all direct children of CHAIN."""
    try:
        children = get_children(chain, password)
        if children:
            for child in children:
                click.echo(child)
        else:
            click.echo(f"No children found for '{chain}'.")
    except LineageError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


@lineage_group.command("ancestors")
@click.argument("chain")
@click.password_option(prompt="Password", confirmation_prompt=False)
def lineage_ancestors(chain, password):
    """Show the ancestor chain for CHAIN (nearest first)."""
    try:
        ancestors = get_ancestors(chain, password)
        if ancestors:
            for anc in ancestors:
                click.echo(anc)
        else:
            click.echo(f"No ancestors found for '{chain}'.")
    except LineageError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)
