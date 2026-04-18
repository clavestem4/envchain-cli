"""CLI commands for chain notes."""
import click
from envchain.notes import set_note, get_note, clear_note


@click.group("notes")
def notes_group():
    """Manage notes/descriptions for chains."""
    pass


@notes_group.command("set")
@click.argument("chain_name")
@click.argument("note")
@click.password_option(prompt="Password", confirmation_prompt=False)
def notes_set(chain_name, note, password):
    """Set a note for a chain."""
    try:
        set_note(chain_name, note, password)
        click.echo(f"Note set for chain '{chain_name}'.")
    except KeyError as e:
        click.echo(str(e), err=True)
        raise SystemExit(1)


@notes_group.command("get")
@click.argument("chain_name")
@click.password_option(prompt="Password", confirmation_prompt=False)
def notes_get(chain_name, password):
    """Get the note for a chain."""
    try:
        note = get_note(chain_name, password)
        if note:
            click.echo(note)
        else:
            click.echo(f"No note set for chain '{chain_name}'.")
    except KeyError as e:
        click.echo(str(e), err=True)
        raise SystemExit(1)


@notes_group.command("clear")
@click.argument("chain_name")
@click.password_option(prompt="Password", confirmation_prompt=False)
def notes_clear(chain_name, password):
    """Clear the note for a chain."""
    try:
        clear_note(chain_name, password)
        click.echo(f"Note cleared for chain '{chain_name}'.")
    except KeyError as e:
        click.echo(str(e), err=True)
        raise SystemExit(1)
