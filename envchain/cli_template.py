"""CLI commands for template rendering."""
import click
from envchain.template import render_template, render_template_file


@click.group(name="template")
def template_group():
    """Render templates using chain variables."""
    pass


@template_group.command(name="render")
@click.argument("chain_name")
@click.option("--password", prompt=True, hide_input=True, help="Chain password.")
@click.option("--file", "template_file", default=None, help="Path to a template file.")
@click.option("--string", "template_str", default=None, help="Inline template string.")
@click.option("--loose", is_flag=True, default=False, help="Allow missing variables (safe_substitute).")
def template_render(chain_name, password, template_file, template_str, loose):
    """Render a template using variables from CHAIN_NAME."""
    if template_file and template_str:
        raise click.UsageError("Provide either --file or --string, not both.")
    if not template_file and not template_str:
        raise click.UsageError("Provide either --file or --string.")

    strict = not loose
    try:
        if template_file:
            result = render_template_file(template_file, chain_name, password, strict=strict)
        else:
            result = render_template(template_str, chain_name, password, strict=strict)
        click.echo(result)
    except KeyError as e:
        raise click.ClickException(f"Missing variable in chain: {e}")
    except Exception as e:
        raise click.ClickException(str(e))
