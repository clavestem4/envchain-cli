"""CLI commands for chain rating."""

import click
from envchain.rating import set_rating, get_rating, clear_rating, list_by_rating, RatingError


@click.group("rating")
def rating_group():
    """Manage chain ratings."""


@rating_group.command("set")
@click.argument("chain")
@click.argument("rating", type=int)
@click.option("--password", envvar="ENVCHAIN_PASSWORD", prompt=True, hide_input=True)
def rating_set(chain, rating, password):
    """Set rating (1-5) for a chain."""
    try:
        set_rating(chain, rating, password)
        click.echo(f"Rating {rating} set for '{chain}'.")
    except RatingError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


@rating_group.command("get")
@click.argument("chain")
@click.option("--password", envvar="ENVCHAIN_PASSWORD", prompt=True, hide_input=True)
def rating_get(chain, password):
    """Get rating for a chain."""
    r = get_rating(chain, password)
    if r is None:
        click.echo(f"No rating set for '{chain}'.")
    else:
        click.echo(f"{chain}: {r}/5")


@rating_group.command("clear")
@click.argument("chain")
@click.option("--password", envvar="ENVCHAIN_PASSWORD", prompt=True, hide_input=True)
def rating_clear(chain, password):
    """Clear rating for a chain."""
    try:
        clear_rating(chain, password)
        click.echo(f"Rating cleared for '{chain}'.")
    except RatingError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


@rating_group.command("list")
@click.option("--min", "min_rating", default=1, type=int, help="Minimum rating filter.")
@click.option("--password", envvar="ENVCHAIN_PASSWORD", prompt=True, hide_input=True)
def rating_list(min_rating, password):
    """List chains by rating."""
    results = list_by_rating(password, min_rating=min_rating)
    if not results:
        click.echo("No rated chains found.")
        return
    for name, r in results:
        stars = "★" * r + "☆" * (5 - r)
        click.echo(f"{name}: {stars} ({r}/5)")
