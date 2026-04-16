"""Export chains to various shell formats."""

from typing import Dict


SUPPORTED_FORMATS = ["bash", "fish", "dotenv"]


def export_bash(env_vars: Dict[str, str]) -> str:
    """Export environment variables as bash export statements."""
    lines = []
    for key, value in env_vars.items():
        escaped = value.replace('"', '\\"')
        lines.append(f'export {key}="{escaped}"')
    return "\n".join(lines)


def export_fish(env_vars: Dict[str, str]) -> str:
    """Export environment variables as fish shell set statements."""
    lines = []
    for key, value in env_vars.items():
        escaped = value.replace('"', '\\"')
        lines.append(f'set -x {key} "{escaped}"')
    return "\n".join(lines)


def export_dotenv(env_vars: Dict[str, str]) -> str:
    """Export environment variables in .env file format."""
    lines = []
    for key, value in env_vars.items():
        escaped = value.replace('"', '\\"')
        lines.append(f'{key}="{escaped}"')
    return "\n".join(lines)


def export_chain(env_vars: Dict[str, str], fmt: str = "bash") -> str:
    """Export a chain's environment variables in the specified format.

    Args:
        env_vars: Dictionary of environment variable key-value pairs.
        fmt: Output format. One of 'bash', 'fish', 'dotenv'.

    Returns:
        Formatted string ready for shell evaluation or file writing.

    Raises:
        ValueError: If the format is not supported.
    """
    if fmt == "bash":
        return export_bash(env_vars)
    elif fmt == "fish":
        return export_fish(env_vars)
    elif fmt == "dotenv":
        return export_dotenv(env_vars)
    else:
        raise ValueError(f"Unsupported format '{fmt}'. Choose from: {', '.join(SUPPORTED_FORMATS)}")
