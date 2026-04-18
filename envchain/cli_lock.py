"""CLI commands for chain locking."""

import click
from envchain.lock import lock_chain, unlock_chain, is_locked, list_locked


@click.group("lock")
def lock_group():
    """Manage chain locks."""


@lock_group.command("add")
@click.argument("chain_name")
@click.password_option(prompt="Password")
def lock_add(chain_name, password):
    """Lock a chain."""
    try:
        lock_chain(chain_name, password)
        click.echo(f"Chain '{chain_name}' locked.")
    except ValueError as e:
        click.echo(str(e), err=True)
        raise SystemExit(1)


@lock_group.command("remove")
@click.argument("chain_name")
@click.password_option(prompt="Password")
def lock_remove(chain_name, password):
    """Unlock a chain."""
    try:
        unlock_chain(chain_name, password)
        click.echo(f"Chain '{chain_name}' unlocked.")
    except ValueError as e:
        click.echo(str(e), err=True)
        raise SystemExit(1)


@lock_group.command("status")
@click.argument("chain_name")
@click.option("--password", prompt=True, hide_input=True)
def lock_status(chain_name, password):
    """Show lock status of a chain."""
    try:
        locked = is_locked(chain_name, password)
        status = "locked" if locked else "unlocked"
        click.echo(f"Chain '{chain_name}' is {status}.")
    except Exception as e:
        click.echo(str(e), err=True)
        raise SystemExit(1)


@lock_group.command("list")
@click.option("--password", prompt=True, hide_input=True)
def lock_list(password):
    """List all locked chains."""
    locked = list_locked(password)
    if not locked:
        click.echo("No locked chains.")
    else:
        for name in locked:
            click.echo(name)
