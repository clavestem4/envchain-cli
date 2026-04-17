"""CLI commands for diffing chains."""
import click
from envchain.chain import get_chain
from envchain.diff import diff_chains, format_diff


@click.group(name="diff")
def diff_group():
    """Compare environment variable chains."""
    pass


@diff_group.command(name="show")
@click.argument("chain_a")
@click.argument("chain_b")
@click.option("--values", is_flag=True, default=False, help="Show variable values in diff.")
@click.option("--store", default=None, help="Path to store file.")
def diff_show(chain_a: str, chain_b: str, values: bool, store: str):
    """Show diff between CHAIN_A and CHAIN_B."""
    kwargs = {"store_path": store} if store else {}
    try:
        vars_a = get_chain(chain_a, **kwargs)
    except KeyError:
        raise click.ClickException(f"Chain '{chain_a}' not found.")
    try:
        vars_b = get_chain(chain_b, **kwargs)
    except KeyError:
        raise click.ClickException(f"Chain '{chain_b}' not found.")

    diff = diff_chains(vars_a, vars_b)
    total_changes = len(diff["added"]) + len(diff["removed"]) + len(diff["modified"])

    click.echo(f"Diff: {chain_a} -> {chain_b}")
    click.echo(format_diff(diff, show_values=values))
    click.echo(f"\n{total_changes} change(s) detected.")
