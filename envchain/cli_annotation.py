"""CLI commands for chain annotations."""

import click
from envchain.annotation import (
    set_annotation,
    remove_annotation,
    get_annotations,
    find_by_annotation,
    AnnotationError,
)
from envchain.chain import get_chain_names


@click.group("annotation")
def annotation_group():
    """Manage freeform annotations on chains."""


@annotation_group.command("set")
@click.argument("chain_name")
@click.argument("key")
@click.argument("value")
@click.password_option("--password", prompt="Password")
def annotation_set(chain_name, key, value, password):
    """Set an annotation KEY=VALUE on CHAIN_NAME."""
    try:
        set_annotation(chain_name, key, value, password)
        click.echo(f"Annotation '{key}' set on '{chain_name}'.")
    except KeyError:
        click.echo(f"Error: Chain '{chain_name}' not found.", err=True)
        raise SystemExit(1)
    except AnnotationError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


@annotation_group.command("remove")
@click.argument("chain_name")
@click.argument("key")
@click.password_option("--password", prompt="Password")
def annotation_remove(chain_name, key, password):
    """Remove annotation KEY from CHAIN_NAME."""
    try:
        remove_annotation(chain_name, key, password)
        click.echo(f"Annotation '{key}' removed from '{chain_name}'.")
    except AnnotationError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


@annotation_group.command("list")
@click.argument("chain_name")
@click.password_option("--password", prompt="Password")
def annotation_list(chain_name, password):
    """List all annotations on CHAIN_NAME."""
    try:
        annotations = get_annotations(chain_name, password)
        if not annotations:
            click.echo("No annotations set.")
        else:
            for k, v in annotations.items():
                click.echo(f"{k}={v}")
    except KeyError:
        click.echo(f"Error: Chain '{chain_name}' not found.", err=True)
        raise SystemExit(1)


@annotation_group.command("find")
@click.argument("key")
@click.option("--value", default=None, help="Filter by annotation value.")
@click.password_option("--password", prompt="Password")
def annotation_find(key, value, password):
    """Find chains that have annotation KEY (optionally matching VALUE)."""
    results = find_by_annotation(key, value, get_chain_names, password)
    if not results:
        click.echo("No chains found.")
    else:
        for name in results:
            click.echo(name)
