"""CLI commands for managing chain variable quotas."""

import click
from envchain.quota import set_quota, get_quota, clear_quota, check_quota, list_over_quota, QuotaError


@click.group("quota")
def quota_group():
    """Manage per-chain variable quotas."""


@quota_group.command("set")
@click.argument("chain_name")
@click.argument("max_vars", type=int)
@click.option("--password", envvar="ENVCHAIN_PASSWORD", prompt=True, hide_input=True)
def quota_set(chain_name, max_vars, password):
    """Set the maximum number of variables for CHAIN_NAME."""
    try:
        set_quota(chain_name, max_vars, password)
        click.echo(f"Quota for '{chain_name}' set to {max_vars} variables.")
    except QuotaError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)
    except KeyError:
        click.echo(f"Error: chain '{chain_name}' not found.", err=True)
        raise SystemExit(1)


@quota_group.command("get")
@click.argument("chain_name")
@click.option("--password", envvar="ENVCHAIN_PASSWORD", prompt=True, hide_input=True)
def quota_get(chain_name, password):
    """Show the quota for CHAIN_NAME."""
    try:
        info = check_quota(chain_name, password)
        limit = info["limit"] if info["limit"] is not None else "unlimited"
        remaining = info["remaining"] if info["remaining"] is not None else "unlimited"
        status = " [EXCEEDED]" if info["exceeded"] else ""
        click.echo(f"Chain: {chain_name}{status}")
        click.echo(f"  Limit    : {limit}")
        click.echo(f"  Used     : {info['used']}")
        click.echo(f"  Remaining: {remaining}")
    except KeyError:
        click.echo(f"Error: chain '{chain_name}' not found.", err=True)
        raise SystemExit(1)


@quota_group.command("clear")
@click.argument("chain_name")
@click.option("--password", envvar="ENVCHAIN_PASSWORD", prompt=True, hide_input=True)
def quota_clear(chain_name, password):
    """Remove quota limit from CHAIN_NAME."""
    try:
        clear_quota(chain_name, password)
        click.echo(f"Quota cleared for '{chain_name}'.")
    except KeyError:
        click.echo(f"Error: chain '{chain_name}' not found.", err=True)
        raise SystemExit(1)


@quota_group.command("list-over")
@click.option("--password", envvar="ENVCHAIN_PASSWORD", prompt=True, hide_input=True)
def quota_list_over(password):
    """List all chains that exceed their quota."""
    over = list_over_quota(password)
    if not over:
        click.echo("No chains are over quota.")
    else:
        click.echo("Chains over quota:")
        for name in over:
            click.echo(f"  - {name}")
