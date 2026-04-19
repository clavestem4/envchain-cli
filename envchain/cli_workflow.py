"""CLI commands for workflow management."""
import click
from envchain.workflow import set_workflow, get_workflow, remove_workflow, list_workflows, WorkflowError


@click.group("workflow")
def workflow_group():
    """Manage ordered chain workflows."""


@workflow_group.command("set")
@click.argument("name")
@click.argument("chains", nargs=-1, required=True)
def workflow_set(name, chains):
    """Define a workflow as an ordered list of chains."""
    try:
        set_workflow(name, list(chains))
        click.echo(f"Workflow '{name}' set with chains: {', '.join(chains)}")
    except WorkflowError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


@workflow_group.command("get")
@click.argument("name")
def workflow_get(name):
    """Show chains in a workflow in order."""
    try:
        chains = get_workflow(name)
        for i, c in enumerate(chains, 1):
            click.echo(f"{i}. {c}")
    except WorkflowError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


@workflow_group.command("remove")
@click.argument("name")
def workflow_remove(name):
    """Remove a workflow."""
    try:
        remove_workflow(name)
        click.echo(f"Workflow '{name}' removed.")
    except WorkflowError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


@workflow_group.command("list")
def workflow_list():
    """List all defined workflows."""
    workflows = list_workflows()
    if not workflows:
        click.echo("No workflows defined.")
        return
    for name, chains in workflows.items():
        click.echo(f"{name}: {' -> '.join(chains)}")
