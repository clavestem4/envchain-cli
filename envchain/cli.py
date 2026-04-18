"""Main CLI entry point for envchain."""

import click
from envchain.chain import add_chain, get_chain, remove_chain, get_chain_names
from envchain.export import export_chain
from envchain.cli_audit import audit_group
from envchain.cli_diff import diff_group
from envchain.cli_snapshot import snapshot_group


@click.group()
def cli():
    """envchain: manage encrypted per-project environment variable sets."""


@cli.command()
@click.argument("chain_name")
@click.argument("password")
@click.argument("env_vars", nargs=-1, required=True)
@click.option("--overwrite", is_flag=True, default=False)
def add(chain_name, password, env_vars, overwrite):
    """Add a new chain with KEY=VALUE pairs."""
    variables = {}
    for pair in env_vars:
        if "=" not in pair:
            raise click.BadParameter(f"Invalid format '{pair}', expected KEY=VALUE.")
        k, v = pair.split("=", 1)
        variables[k] = v
    add_chain(chain_name, variables, password, overwrite=overwrite)
    click.echo(f"Chain '{chain_name}' saved.")


@cli.command()
@click.argument("chain_name")
@click.argument("password")
@click.option("--format", "fmt", default="bash", type=click.Choice(["bash", "fish", "dotenv"]), show_default=True)
@click.option("--export", "do_export", is_flag=True, default=False)
def get(chain_name, password, fmt, do_export):
    """Get and display variables for a chain."""
    try:
        if do_export:
            output = export_chain(chain_name, password, fmt)
            click.echo(output)
        else:
            variables = get_chain(chain_name, password)
            for k, v in variables.items():
                click.echo(f"{k}={v}")
    except Exception as e:
        raise click.ClickException(str(e))


@cli.command()
@click.argument("chain_name")
@click.argument("password")
def remove(chain_name, password):
    """Remove a chain."""
    try:
        remove_chain(chain_name, password)
        click.echo(f"Chain '{chain_name}' removed.")
    except Exception as e:
        raise click.ClickException(str(e))


@cli.command(name="list")
def list_chains():
    """List all available chains."""
    names = get_chain_names()
    if not names:
        click.echo("No chains found.")
    else:
        for name in names:
            click.echo(name)


cli.add_command(audit_group)
cli.add_command(diff_group)
cli.add_command(snapshot_group)
