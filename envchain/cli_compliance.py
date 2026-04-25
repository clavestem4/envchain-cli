"""CLI commands for compliance tagging."""

import click
from envchain.compliance import (
    set_compliance,
    remove_compliance,
    get_compliance,
    list_by_compliance,
    ComplianceError,
    VALID_STANDARDS,
)


@click.group("compliance")
def compliance_group():
    """Manage compliance tags on chains."""


@compliance_group.command("set")
@click.argument("chain_name")
@click.argument("standard")
@click.option("--note", default="", help="Optional note about this compliance tag.")
@click.option("--password", default="", envvar="ENVCHAIN_PASSWORD", help="Encryption password.")
def compliance_set(chain_name, standard, note, password):
    """Tag CHAIN_NAME with a compliance STANDARD."""
    try:
        set_compliance(chain_name, standard, note=note, password=password)
        click.echo(f"Compliance '{standard}' set on '{chain_name}'.")
    except ComplianceError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


@compliance_group.command("remove")
@click.argument("chain_name")
@click.argument("standard")
@click.option("--password", default="", envvar="ENVCHAIN_PASSWORD", help="Encryption password.")
def compliance_remove(chain_name, standard, password):
    """Remove a compliance STANDARD tag from CHAIN_NAME."""
    try:
        remove_compliance(chain_name, standard, password=password)
        click.echo(f"Compliance '{standard}' removed from '{chain_name}'.")
    except ComplianceError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


@compliance_group.command("get")
@click.argument("chain_name")
@click.option("--password", default="", envvar="ENVCHAIN_PASSWORD", help="Encryption password.")
def compliance_get(chain_name, password):
    """Show compliance tags for CHAIN_NAME."""
    tags = get_compliance(chain_name, password=password)
    if not tags:
        click.echo(f"No compliance tags set on '{chain_name}'.")
        return
    for standard, meta in tags.items():
        note = meta.get("note", "")
        line = f"  {standard}"
        if note:
            line += f": {note}"
        click.echo(line)


@compliance_group.command("list")
@click.argument("standard")
@click.option("--password", default="", envvar="ENVCHAIN_PASSWORD", help="Encryption password.")
def compliance_list(standard, password):
    """List all chains tagged with STANDARD."""
    if standard not in VALID_STANDARDS:
        click.echo(f"Error: Unknown standard '{standard}'.", err=True)
        raise SystemExit(1)
    chains = list_by_compliance(standard, password=password)
    if not chains:
        click.echo(f"No chains tagged with '{standard}'.")
        return
    for name in chains:
        click.echo(name)
