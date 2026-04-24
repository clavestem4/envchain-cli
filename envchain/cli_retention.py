"""CLI commands for retention policy management."""

import click
from envchain.retention import (
    RetentionError,
    set_retention,
    get_retention,
    clear_retention,
    is_retention_expired,
    list_expired_retention,
)


@click.group("retention")
def retention_group():
    """Manage retention policies for chains."""


@retention_group.command("set")
@click.argument("chain_name")
@click.argument("days", type=int)
@click.password_option("--password", "-p", prompt="Password")
def retention_set(chain_name, days, password):
    """Set retention policy (in days) for CHAIN_NAME."""
    try:
        set_retention(chain_name, days, password)
        click.echo(f"Retention policy set: {chain_name} expires after {days} day(s).")
    except RetentionError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)
    except KeyError:
        click.echo(f"Error: chain '{chain_name}' not found.", err=True)
        raise SystemExit(1)


@retention_group.command("get")
@click.argument("chain_name")
@click.password_option("--password", "-p", prompt="Password")
def retention_get(chain_name, password):
    """Show retention policy for CHAIN_NAME."""
    try:
        days = get_retention(chain_name, password)
        if days is None:
            click.echo(f"No retention policy set for '{chain_name}'.")
        else:
            expired = is_retention_expired(chain_name, password)
            status = " [EXPIRED]" if expired else ""
            click.echo(f"{chain_name}: {days} day(s){status}")
    except KeyError:
        click.echo(f"Error: chain '{chain_name}' not found.", err=True)
        raise SystemExit(1)


@retention_group.command("clear")
@click.argument("chain_name")
@click.password_option("--password", "-p", prompt="Password")
def retention_clear(chain_name, password):
    """Remove retention policy from CHAIN_NAME."""
    try:
        clear_retention(chain_name, password)
        click.echo(f"Retention policy cleared for '{chain_name}'.")
    except KeyError:
        click.echo(f"Error: chain '{chain_name}' not found.", err=True)
        raise SystemExit(1)


@retention_group.command("expired")
@click.password_option("--password", "-p", prompt="Password")
def retention_expired(password):
    """List all chains whose retention period has expired."""
    expired = list_expired_retention(password)
    if not expired:
        click.echo("No chains with expired retention.")
    else:
        for name in expired:
            click.echo(name)
