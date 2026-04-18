import click
from envchain.chain import add_chain, get_chain, remove_chain, get_chain_names
from envchain.export import export_chain
from envchain.cli_audit import audit_group
from envchain.cli_diff import diff_group
from envchain.cli_snapshot import snapshot_group
from envchain.cli_template import template_group
from envchain.cli_history import history_group
from envchain.cli_pin import pin_group
from envchain.cli_notes import notes_group
from envchain.cli_lock import lock_group
from envchain.cli_watch import watch_group
from envchain.cli_alias import alias_group


@click.group()
def cli():
    """envchain — per-project encrypted environment variable manager."""


cli.add_command(audit_group)
cli.add_command(diff_group)
cli.add_command(snapshot_group)
cli.add_command(template_group)
cli.add_command(history_group)
cli.add_command(pin_group)
cli.add_command(notes_group)
cli.add_command(lock_group)
cli.add_command(watch_group)
cli.add_command(alias_group)


@cli.command()
@click.argument("chain")
@click.argument("vars", nargs=-1)
@click.password_option()
def add(chain, vars, password):
    """Add or update a chain with KEY=VALUE pairs."""
    parsed = {}
    for v in vars:
        if "=" not in v:
            raise click.BadParameter(f"Invalid format '{v}', expected KEY=VALUE")
        k, val = v.split("=", 1)
        parsed[k] = val
    add_chain(chain, password, parsed)
    click.echo(f"Chain '{chain}' saved.")


@cli.command()
@click.argument("chain")
@click.option("--format", "fmt", default="bash", type=click.Choice(["bash", "fish", "dotenv"]))
@click.password_option(prompt="Password", confirmation_prompt=False)
def get(chain, fmt, password):
    """Get and export a chain."""
    click.echo(export_chain(chain, password, fmt))


@cli.command()
@click.argument("chain")
def remove(chain):
    """Remove a chain."""
    remove_chain(chain)
    click.echo(f"Chain '{chain}' removed.")


@cli.command(name="list")
def list_chains():
    """List all chains."""
    names = get_chain_names()
    if not names:
        click.echo("No chains found.")
    for name in names:
        click.echo(name)
