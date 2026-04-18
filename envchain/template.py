"""Template rendering for environment variable chains."""
from string import Template
from typing import Optional
from envchain.chain import get_chain


def render_template(template_str: str, chain_name: str, password: str, strict: bool = True) -> str:
    """Render a template string substituting variables from a chain.

    Args:
        template_str: A string with $VAR or ${VAR} placeholders.
        chain_name: The chain to load variables from.
        password: Password to decrypt the chain.
        strict: If True, raise KeyError on missing variables.

    Returns:
        Rendered string with substitutions applied.
    """
    chain = get_chain(chain_name, password)
    tmpl = Template(template_str)
    if strict:
        return tmpl.substitute(chain)
    return tmpl.safe_substitute(chain)


def render_template_file(path: str, chain_name: str, password: str, strict: bool = True) -> str:
    """Read a template file and render it using variables from a chain.

    Args:
        path: Path to the template file.
        chain_name: The chain to load variables from.
        password: Password to decrypt the chain.
        strict: If True, raise KeyError on missing variables.

    Returns:
        Rendered string.
    """
    with open(path, "r") as f:
        template_str = f.read()
    return render_template(template_str, chain_name, password, strict=strict)
