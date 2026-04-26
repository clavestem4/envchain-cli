import click
from envchain.sensitivity import (
    set_sensitivity,
    get_sensitivity,
    clear_sensitivity,
    list_by_sensitivity,
    SensitivityError,
    VALID_LEVELS,
)
from envchain.chain import get_chain, add_chain, get_chain_names


@click.group("sensitivity")
def sensitivity_group():
    """Manage sensitivity levels for chains."""


@sensitivity_group.command("set")
@click.argument("chain_name")
@click.argument("level")
@click.option("--password", prompt=True, hide_input=True)
def sensitivity_set(chain_name, level, password):
    """Set the sensitivity level for a chain."""
    try:
        set_sensitivity(chain_name, level, password, get_chain, add_chain)
        click.echo(f"Sensitivity for '{chain_name}' set to '{level}'.")
    except SensitivityError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


@sensitivity_group.command("get")
@click.argument("chain_name")
@click.option("--password", prompt=True, hide_input=True)
def sensitivity_get(chain_name, password):
    """Get the sensitivity level of a chain."""
    try:
        level = get_sensitivity(chain_name, password, get_chain)
        if level:
            click.echo(f"{chain_name}: {level}")
        else:
            click.echo(f"{chain_name}: (not set)")
    except SensitivityError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


@sensitivity_group.command("clear")
@click.argument("chain_name")
@click.option("--password", prompt=True, hide_input=True)
def sensitivity_clear(chain_name, password):
    """Clear the sensitivity level of a chain."""
    try:
        clear_sensitivity(chain_name, password, get_chain, add_chain)
        click.echo(f"Sensitivity for '{chain_name}' cleared.")
    except SensitivityError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


@sensitivity_group.command("list")
@click.argument("level")
@click.option("--password", prompt=True, hide_input=True)
def sensitivity_list(level, password):
    """List chains with a given sensitivity level."""
    try:
        chains = list_by_sensitivity(level, password, get_chain_names, get_chain)
        if chains:
            for name in chains:
                click.echo(name)
        else:
            click.echo(f"No chains with sensitivity '{level}'.")
    except SensitivityError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)
