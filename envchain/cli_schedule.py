"""CLI commands for chain scheduling."""
import click
from envchain.schedule import set_schedule, get_schedule, clear_schedule, list_scheduled
from envchain.chain import get_chain_names


@click.group("schedule")
def schedule_group():
    """Manage refresh schedules for chains."""
    pass


@schedule_group.command("set")
@click.argument("chain_name")
@click.argument("interval", type=click.Choice(["hourly", "daily", "weekly"]))
@click.password_option("--password", prompt="Password")
def schedule_set(chain_name, interval, password):
    """Set a refresh schedule on a chain."""
    try:
        set_schedule(chain_name, interval, password)
        click.echo(f"Schedule '{interval}' set for chain '{chain_name}'.")
    except KeyError:
        click.echo(f"Error: chain '{chain_name}' not found.", err=True)
        raise SystemExit(1)
    except ValueError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


@schedule_group.command("get")
@click.argument("chain_name")
@click.password_option("--password", prompt="Password")
def schedule_get(chain_name, password):
    """Show the schedule for a chain."""
    try:
        interval = get_schedule(chain_name, password)
        if interval:
            click.echo(f"{chain_name}: {interval}")
        else:
            click.echo(f"No schedule set for '{chain_name}'.")
    except KeyError:
        click.echo(f"Error: chain '{chain_name}' not found.", err=True)
        raise SystemExit(1)


@schedule_group.command("clear")
@click.argument("chain_name")
@click.password_option("--password", prompt="Password")
def schedule_clear(chain_name, password):
    """Remove the schedule from a chain."""
    try:
        clear_schedule(chain_name, password)
        click.echo(f"Schedule cleared for '{chain_name}'.")
    except KeyError:
        click.echo(f"Error: chain '{chain_name}' not found.", err=True)
        raise SystemExit(1)


@schedule_group.command("list")
@click.password_option("--password", prompt="Password")
def schedule_list(password):
    """List all chains with a schedule."""
    names = get_chain_names(password)
    scheduled = list_scheduled(names, password)
    if not scheduled:
        click.echo("No scheduled chains.")
    else:
        for name, interval in scheduled:
            click.echo(f"{name}: {interval}")
