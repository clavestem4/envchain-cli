import click
from envchain.confidence import (
    set_confidence,
    get_confidence,
    clear_confidence,
    list_by_confidence,
    VALID_LEVELS,
    ConfidenceError,
)


@click.group("confidence")
def confidence_group():
    """Manage confidence levels for chains."""


@confidence_group.command("set")
@click.argument("chain_name")
@click.argument("level", type=click.Choice(sorted(VALID_LEVELS)))
@click.password_option()
def confidence_set(chain_name, level, password):
    """Set the confidence level for CHAIN_NAME."""
    try:
        set_confidence(chain_name, level, password)
        click.echo(f"Confidence level '{level}' set on chain '{chain_name}'.")
    except ConfidenceError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


@confidence_group.command("get")
@click.argument("chain_name")
@click.password_option()
def confidence_get(chain_name, password):
    """Get the confidence level for CHAIN_NAME."""
    try:
        level = get_confidence(chain_name, password)
        if level is None:
            click.echo(f"No confidence level set on chain '{chain_name}'.")
        else:
            click.echo(level)
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


@confidence_group.command("clear")
@click.argument("chain_name")
@click.password_option()
def confidence_clear(chain_name, password):
    """Clear the confidence level from CHAIN_NAME."""
    try:
        clear_confidence(chain_name, password)
        click.echo(f"Confidence level cleared from chain '{chain_name}'.")
    except ConfidenceError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


@confidence_group.command("list")
@click.option("--level", type=click.Choice(sorted(VALID_LEVELS)), default=None)
@click.password_option()
def confidence_list(level, password):
    """List chains with confidence levels, optionally filtered by LEVEL."""
    mapping = list_by_confidence(password, level=level)
    if not mapping:
        click.echo("No chains with confidence levels found.")
        return
    for name, lvl in sorted(mapping.items()):
        click.echo(f"{name}: {lvl}")
