"""CLI commands for chain label management."""

import click
from envchain.label import set_label, remove_label, get_labels, find_by_label, LabelError
from envchain.chain import get_chain


@click.group("label")
def label_group():
    """Manage key/value labels on chains."""


@label_group.command("set")
@click.argument("chain_name")
@click.argument("key")
@click.argument("value")
@click.password_option(prompt="Password")
def label_set(chain_name, key, value, password):
    """Set a label KEY=VALUE on a chain."""
    try:
        set_label(chain_name, key, value, password)
        click.echo(f"Label '{key}={value}' set on '{chain_name}'.")
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


@label_group.command("remove")
@click.argument("chain_name")
@click.argument("key")
@click.password_option(prompt="Password")
def label_remove(chain_name, key, password):
    """Remove a label from a chain."""
    try:
        remove_label(chain_name, key, password)
        click.echo(f"Label '{key}' removed from '{chain_name}'.")
    except LabelError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


@label_group.command("list")
@click.argument("chain_name")
@click.password_option(prompt="Password")
def label_list(chain_name, password):
    """List all labels on a chain."""
    try:
        labels = get_labels(chain_name, password)
        if not labels:
            click.echo("No labels set.")
        else:
            for k, v in labels.items():
                click.echo(f"  {k}={v}")
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


@label_group.command("find")
@click.argument("key")
@click.argument("value")
@click.password_option(prompt="Password")
def label_find(key, value, password):
    """Find chains with a matching label KEY=VALUE."""
    results = find_by_label(key, value, password)
    if not results:
        click.echo("No chains found.")
    else:
        for name in results:
            click.echo(name)
