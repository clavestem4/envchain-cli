"""CLI commands for chain drift detection."""
import click
import json
from envchain.watch import snapshot_chain, detect_drift, format_drift_report, has_drift


@click.group(name="watch")
def watch_group():
    """Detect drift in chain variables."""


@watch_group.command(name="snapshot")
@click.argument("chain_name")
@click.password_option(prompt="Password", confirmation_prompt=False)
def watch_snapshot(chain_name: str, password: str):
    """Print a JSON snapshot of the current chain state."""
    try:
        snap = snapshot_chain(chain_name, password)
        click.echo(json.dumps(snap, indent=2))
    except KeyError:
        click.echo(f"Error: chain '{chain_name}' not found.", err=True)
        raise SystemExit(1)


@watch_group.command(name="diff")
@click.argument("chain_name")
@click.argument("baseline_file", type=click.Path(exists=True))
@click.password_option(prompt="Password", confirmation_prompt=False)
@click.option("--json", "as_json", is_flag=True, help="Output as JSON")
def watch_diff(chain_name: str, baseline_file: str, password: str, as_json: bool):
    """Compare current chain state against a saved baseline snapshot."""
    try:
        with open(baseline_file) as f:
            baseline = json.load(f)
    except (json.JSONDecodeError, OSError) as e:
        click.echo(f"Error reading baseline: {e}", err=True)
        raise SystemExit(1)

    try:
        drift = detect_drift(chain_name, password, baseline)
    except KeyError:
        click.echo(f"Error: chain '{chain_name}' not found.", err=True)
        raise SystemExit(1)

    if as_json:
        click.echo(json.dumps(drift, indent=2))
    else:
        click.echo(format_drift_report(chain_name, drift))

    if has_drift(drift):
        raise SystemExit(2)
