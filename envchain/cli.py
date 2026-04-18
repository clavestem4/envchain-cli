"""Main CLI entry point for envchain."""
import click
from envchain.chain import add_chain, get_chain, remove_chain, get_chain_names
from envchain.export import export_chain
from envchain.cli_audit import audit_group
from envchain.cli_diff import diff_group
from envchain.cli_snapshot import snapshot_group
from envchain.cli_template import template_group
from envchain.cli_history import history_group
from envchain.cli_pin import pin_group


@click.group()
def cli():
    """envchain — manage encrypted per-project environment variable sets."""
    pass


@cli.command()
@click.argument("name")
@click.argument("envvars", nargs=-1, required=True)
@click.option("--overwrite", is_flag=True, default=False)
def add(name, envvars, overwrite):
    """Add a chain with KEY=VALUE pairs."""
    data = {}
    for item in envvars:
        if "=" not in item:
            click.echo(f"Invalid format: '{item}'. Use KEY=VALUE.", err=True)
            raise SystemExit(1)
        k, v = item.split("=", 1)
        data[k] = v
    add_chain(name, data, overwrite=overwrite)
    click.echo(f"Chain '{name}' saved.")


@cli.command()
@click.argument("name")
@click.option("--export", "fmt", default=None, type=click.Choice(["bash", "fish", "dotenv"]))
def get(name, fmt):
    """Get a chain's variables."""
    try:
        if fmt:
            click.echo(export_chain(name, fmt))
        else:
            chain = get_chain(name)
            for k, v in chain.items():
                click.echo(f"{k}={v}")
    except KeyError:
        click.echo(f"Chain '{name}' not found.", err=True)
        raise SystemExit(1)


@cli.command()
@click.argument("name")
def remove(name):
    """Remove a chain."""
    try:
        remove_chain(name)
        click.echo(f"Chain '{name}' removed.")
    except KeyError:
        click.echo(f"Chain '{name}' not found.", err=True)
        raise SystemExit(1)


@cli.command(name="list")
def list_chains():
    """List all chains."""
    names = get_chain_names()
    if not names:
        click.echo("No chains found.")
    else:
        for n in names:
            click.echo(n)


cli.add_command(audit_group)
cli.add_command(diff_group)
cli.add_command(snapshot_group)
cli.add_command(template_group)
cli.add_command(history_group)
cli.add_command(pin_group)
