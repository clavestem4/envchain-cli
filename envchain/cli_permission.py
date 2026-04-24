"""CLI commands for managing chain permissions."""

import click
from envchain.permission import (
    PermissionError,
    set_permission,
    get_permission,
    revoke_permission,
    list_permissions,
    find_chains_for_user,
    VALID_PERMISSIONS,
)


@click.group("permission")
def permission_group():
    """Manage per-user permissions on chains."""


@permission_group.command("set")
@click.argument("chain")
@click.argument("user")
@click.argument("perms", nargs=-1, required=True)
def permission_set(chain, user, perms):
    """Set permissions (read/write/exec) for USER on CHAIN."""
    try:
        set_permission(chain, user, list(perms))
        click.echo(f"Permissions for '{user}' on '{chain}': {', '.join(sorted(perms))}")
    except PermissionError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)
    except KeyError:
        click.echo(f"Error: chain '{chain}' not found.", err=True)
        raise SystemExit(1)


@permission_group.command("get")
@click.argument("chain")
@click.argument("user")
def permission_get(chain, user):
    """Get permissions for USER on CHAIN."""
    try:
        perms = get_permission(chain, user)
        if perms:
            click.echo(f"{user}: {', '.join(perms)}")
        else:
            click.echo(f"{user} has no permissions on '{chain}'.")
    except KeyError:
        click.echo(f"Error: chain '{chain}' not found.", err=True)
        raise SystemExit(1)


@permission_group.command("revoke")
@click.argument("chain")
@click.argument("user")
def permission_revoke(chain, user):
    """Revoke all permissions for USER on CHAIN."""
    try:
        revoke_permission(chain, user)
        click.echo(f"Revoked permissions for '{user}' on '{chain}'.")
    except PermissionError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)
    except KeyError:
        click.echo(f"Error: chain '{chain}' not found.", err=True)
        raise SystemExit(1)


@permission_group.command("list")
@click.argument("chain")
def permission_list(chain):
    """List all permissions on CHAIN."""
    try:
        perms = list_permissions(chain)
        if not perms:
            click.echo(f"No permissions set on '{chain}'.")
        else:
            for user, p in perms.items():
                click.echo(f"  {user}: {', '.join(p)}")
    except KeyError:
        click.echo(f"Error: chain '{chain}' not found.", err=True)
        raise SystemExit(1)


@permission_group.command("find")
@click.argument("user")
@click.option("--perm", default=None, help="Filter by specific permission.")
def permission_find(user, perm):
    """Find chains where USER has permissions."""
    chains = find_chains_for_user(user, perm)
    if not chains:
        click.echo(f"No chains found for user '{user}'.")
    else:
        for name in chains:
            click.echo(f"  {name}")
