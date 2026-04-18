"""CLI commands for key rotation."""

import click
from envchain.rotate import rotate_chain, rotate_all, RotationError
from envchain.chain import get_chain_names


@click.group("rotate")
def rotate_group():
    """Rotate encryption password for chains."""


@rotate_group.command("chain")
@click.argument("chain_name")
@click.option("--old-password", prompt=True, hide_input=True, help="Current password")
@click.option("--new-password", prompt=True, hide_input=True, confirmation_prompt=True, help="New password")
def rotate_one(chain_name, old_password, new_password):
    """Re-encrypt CHAIN_NAME under a new password."""
    try:
        rotate_chain(chain_name, old_password, new_password)
        click.echo(f"Chain '{chain_name}' successfully re-encrypted.")
    except RotationError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


@rotate_group.command("all")
@click.option("--old-password", prompt=True, hide_input=True, help="Current password")
@click.option("--new-password", prompt=True, hide_input=True, confirmation_prompt=True, help="New password")
def rotate_all_cmd(old_password, new_password):
    """Re-encrypt ALL chains under a new password."""
    names = get_chain_names()
    if not names:
        click.echo("No chains found.")
        return
    results = rotate_all(names, old_password, new_password)
    for name, result in results.items():
        if result["status"] == "ok":
            click.echo(f"  [ok]    {name}")
        else:
            click.echo(f"  [fail]  {name}: {result['reason']}", err=True)
