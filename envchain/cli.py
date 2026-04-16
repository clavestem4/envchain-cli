import sys
import click
from envchain.chain import add_chain, get_chain, remove_chain, get_chain_names


@click.group()
def cli():
    """envchain-cli: Manage encrypted per-project environment variable sets."""
    pass


@cli.command("add")
@click.argument("chain_name")
@click.option("--password", prompt=True, hide_input=True, confirmation_prompt=True,
              help="Password to encrypt the chain.")
@click.option("--env", "-e", multiple=True, metavar="KEY=VALUE",
              help="Environment variable in KEY=VALUE format.")
def add(chain_name, password, env):
    """Add a new chain with environment variables."""
    variables = {}
    for item in env:
        if "=" not in item:
            click.echo(f"Invalid format '{item}'. Use KEY=VALUE.", err=True)
            sys.exit(1)
        key, _, value = item.partition("=")
        variables[key.strip()] = value.strip()

    if not variables:
        click.echo("No variables provided. Use -e KEY=VALUE.", err=True)
        sys.exit(1)

    add_chain(chain_name, variables, password)
    click.echo(f"Chain '{chain_name}' saved with {len(variables)} variable(s).")


@cli.command("get")
@click.argument("chain_name")
@click.option("--password", prompt=True, hide_input=True,
              help="Password to decrypt the chain.")
@click.option("--export", is_flag=True, default=False,
              help="Print variables as export statements.")
def get(chain_name, password, export):
    """Retrieve and display environment variables from a chain."""
    variables = get_chain(chain_name, password)
    for key, value in variables.items():
        if export:
            click.echo(f"export {key}={value}")
        else:
            click.echo(f"{key}={value}")


@cli.command("remove")
@click.argument("chain_name")
@click.confirmation_option(prompt="Are you sure you want to remove this chain?")
def remove(chain_name):
    """Remove a chain from the store."""
    remove_chain(chain_name)
    click.echo(f"Chain '{chain_name}' removed.")


@cli.command("list")
def list_chains():
    """List all available chain names."""
    names = get_chain_names()
    if not names:
        click.echo("No chains found.")
    else:
        for name in names:
            click.echo(name)


if __name__ == "__main__":
    cli()
