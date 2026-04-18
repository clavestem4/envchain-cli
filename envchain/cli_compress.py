"""CLI commands for chain compression."""

import click
from envchain.compress import compress_chain, decompress_chain, compressed_size, CompressError


@click.group("compress")
def compress_group():
    """Compress and decompress chains for compact sharing."""
    pass


@compress_group.command("pack")
@click.argument("chain_name")
@click.option("--password", prompt=True, hide_input=True, help="Encryption password")
def pack(chain_name, password):
    """Compress a chain into a portable blob."""
    try:
        blob = compress_chain(chain_name, password)
        size = compressed_size(blob)
        click.echo(f"Compressed '{chain_name}' ({size} bytes):")
        click.echo(blob)
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


@compress_group.command("unpack")
@click.argument("blob")
@click.option("--password", prompt=True, hide_input=True, help="Encryption password")
@click.option("--name", default=None, help="Override chain name on import")
@click.option("--overwrite", is_flag=True, default=False, help="Overwrite existing chain")
def unpack(blob, password, name, overwrite):
    """Decompress and import a chain from a blob."""
    try:
        chain_name = decompress_chain(blob, password, new_name=name, overwrite=overwrite)
        click.echo(f"Chain '{chain_name}' imported successfully.")
    except CompressError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)
