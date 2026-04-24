"""CLI commands for checkpoint management."""

import click
from envchain.checkpoint import (
    save_checkpoint,
    restore_checkpoint,
    list_checkpoints,
    delete_checkpoint,
    CheckpointError,
)


@click.group("checkpoint")
def checkpoint_group():
    """Manage named restore points (checkpoints) for chains."""


@checkpoint_group.command("save")
@click.argument("chain")
@click.argument("label")
@click.password_option("--password", "-p", prompt=True)
def checkpoint_save(chain, label, password):
    """Save current state of CHAIN as checkpoint LABEL."""
    try:
        info = save_checkpoint(chain, label, password)
        click.echo(f"Checkpoint '{label}' saved at {info['saved_at']}.")
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


@checkpoint_group.command("restore")
@click.argument("chain")
@click.argument("label")
@click.password_option("--password", "-p", prompt=True)
def checkpoint_restore(chain, label, password):
    """Restore CHAIN to the state saved under checkpoint LABEL."""
    try:
        vars_ = restore_checkpoint(chain, label, password)
        click.echo(f"Restored {len(vars_)} variable(s) from checkpoint '{label}'.")
    except CheckpointError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


@checkpoint_group.command("list")
@click.argument("chain")
@click.password_option("--password", "-p", prompt=True)
def checkpoint_list(chain, password):
    """List all checkpoints for CHAIN."""
    try:
        checkpoints = list_checkpoints(chain, password)
        if not checkpoints:
            click.echo("No checkpoints found.")
            return
        for label, info in checkpoints.items():
            click.echo(f"  {label}  (saved: {info['saved_at']}, vars: {len(info['vars'])})")
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


@checkpoint_group.command("delete")
@click.argument("chain")
@click.argument("label")
@click.password_option("--password", "-p", prompt=True)
def checkpoint_delete(chain, label, password):
    """Delete checkpoint LABEL from CHAIN."""
    try:
        delete_checkpoint(chain, label, password)
        click.echo(f"Checkpoint '{label}' deleted.")
    except CheckpointError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)
