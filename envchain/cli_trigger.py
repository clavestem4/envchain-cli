"""CLI commands for managing chain event triggers."""

import click
from envchain.trigger import (
    set_trigger,
    get_trigger,
    remove_trigger,
    list_triggers,
    find_chains_with_trigger,
    TriggerError,
    VALID_EVENTS,
)
from envchain.chain import get_chain  # for existence check


@click.group("trigger")
def trigger_group():
    """Manage event-based command triggers on chains."""


@trigger_group.command("set")
@click.argument("chain_name")
@click.argument("event", type=click.Choice(sorted(VALID_EVENTS)))
@click.argument("command")
def trigger_set(chain_name, event, command):
    """Attach COMMAND to EVENT on CHAIN_NAME."""
    try:
        set_trigger(chain_name, event, command)
        click.echo(f"Trigger set: [{chain_name}] {event} -> {command}")
    except KeyError:
        click.echo(f"Error: chain '{chain_name}' not found.", err=True)
        raise SystemExit(1)
    except TriggerError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


@trigger_group.command("get")
@click.argument("chain_name")
@click.argument("event", type=click.Choice(sorted(VALID_EVENTS)))
def trigger_get(chain_name, event):
    """Show the command for EVENT on CHAIN_NAME."""
    try:
        cmd = get_trigger(chain_name, event)
        if cmd is None:
            click.echo(f"No trigger set for event '{event}' on '{chain_name}'.")
        else:
            click.echo(cmd)
    except KeyError:
        click.echo(f"Error: chain '{chain_name}' not found.", err=True)
        raise SystemExit(1)


@trigger_group.command("remove")
@click.argument("chain_name")
@click.argument("event", type=click.Choice(sorted(VALID_EVENTS)))
def trigger_remove(chain_name, event):
    """Remove the trigger for EVENT on CHAIN_NAME."""
    try:
        remove_trigger(chain_name, event)
        click.echo(f"Trigger '{event}' removed from '{chain_name}'.")
    except (KeyError, TriggerError) as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


@trigger_group.command("list")
@click.argument("chain_name")
def trigger_list(chain_name):
    """List all triggers for CHAIN_NAME."""
    try:
        triggers = list_triggers(chain_name)
        if not triggers:
            click.echo(f"No triggers set for '{chain_name}'.")
        else:
            for event, cmd in sorted(triggers.items()):
                click.echo(f"  {event}: {cmd}")
    except KeyError:
        click.echo(f"Error: chain '{chain_name}' not found.", err=True)
        raise SystemExit(1)


@trigger_group.command("find")
@click.argument("event", type=click.Choice(sorted(VALID_EVENTS)))
def trigger_find(event):
    """Find all chains that have a trigger for EVENT."""
    chains = find_chains_with_trigger(event)
    if not chains:
        click.echo(f"No chains have a trigger for '{event}'.")
    else:
        for name in chains:
            click.echo(name)
