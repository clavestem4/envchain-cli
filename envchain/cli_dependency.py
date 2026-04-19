"""CLI commands for chain dependency management."""

import click
from envchain.dependency import (
    set_dependencies, get_dependencies, clear_dependencies, resolve_order, DependencyError
)


@click.group("deps")
def deps_group():
    """Manage chain dependencies."""


@deps_group.command("set")
@click.argument("name")
@click.argument("deps", nargs=-1, required=True)
@click.option("--password", envvar="ENVCHAIN_PASSWORD", prompt=True, hide_input=True)
def deps_set(name, deps, password):
    """Set dependencies for a chain."""
    try:
        set_dependencies(name, list(deps), password)
        click.echo(f"Dependencies for '{name}' set to: {', '.join(deps)}")
    except DependencyError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


@deps_group.command("get")
@click.argument("name")
@click.option("--password", envvar="ENVCHAIN_PASSWORD", prompt=True, hide_input=True)
def deps_get(name, password):
    """Show dependencies for a chain."""
    deps = get_dependencies(name, password)
    if deps:
        click.echo("\n".join(deps))
    else:
        click.echo(f"No dependencies set for '{name}'.")


@deps_group.command("clear")
@click.argument("name")
@click.option("--password", envvar="ENVCHAIN_PASSWORD", prompt=True, hide_input=True)
def deps_clear(name, password):
    """Clear dependencies for a chain."""
    clear_dependencies(name, password)
    click.echo(f"Dependencies cleared for '{name}'.")


@deps_group.command("order")
@click.argument("names", nargs=-1, required=True)
@click.option("--password", envvar="ENVCHAIN_PASSWORD", prompt=True, hide_input=True)
def deps_order(names, password):
    """Resolve load order for chains respecting dependencies."""
    try:
        order = resolve_order(list(names), password)
        click.echo("\n".join(order))
    except DependencyError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)
