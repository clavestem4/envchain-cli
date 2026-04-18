"""CLI commands for snapshot management."""

import click
from envchain.chain import get_chain, add_chain
from envchain.snapshot import save_snapshot, load_snapshot, list_snapshots, delete_snapshot


@click.group("snapshot")
def snapshot_group():
    """Manage snapshots of environment chains."""


@snapshot_group.command("save")
@click.argument("chain_name")
@click.argument("password")
@click.option("--name", default=None, help="Snapshot name (default: timestamp)")
def snapshot_save(chain_name, password, name):
    """Save a snapshot of a chain."""
    try:
        variables = get_chain(chain_name, password)
    except Exception as e:
        raise click.ClickException(str(e))
    snapshot_name = save_snapshot(chain_name, variables, name)
    click.echo(f"Snapshot '{snapshot_name}' saved for chain '{chain_name}'.")


@snapshot_group.command("restore")
@click.argument("chain_name")
@click.argument("snapshot_name")
@click.argument("password")
@click.option("--overwrite", is_flag=True, default=False, help="Overwrite existing chain.")
def snapshot_restore(chain_name, snapshot_name, password, overwrite):
    """Restore a chain from a snapshot."""
    try:
        variables = load_snapshot(chain_name, snapshot_name)
        add_chain(chain_name, variables, password, overwrite=overwrite)
    except FileNotFoundError as e:
        raise click.ClickException(str(e))
    except Exception as e:
        raise click.ClickException(str(e))
    click.echo(f"Chain '{chain_name}' restored from snapshot '{snapshot_name}'.")


@snapshot_group.command("list")
@click.argument("chain_name")
def snapshot_list(chain_name):
    """List snapshots for a chain."""
    names = list_snapshots(chain_name)
    if not names:
        click.echo(f"No snapshots found for chain '{chain_name}'.")
    else:
        for name in names:
            click.echo(name)


@snapshot_group.command("delete")
@click.argument("chain_name")
@click.argument("snapshot_name")
def snapshot_delete(chain_name, snapshot_name):
    """Delete a snapshot."""
    try:
        delete_snapshot(chain_name, snapshot_name)
    except FileNotFoundError as e:
        raise click.ClickException(str(e))
    click.echo(f"Snapshot '{snapshot_name}' deleted.")
