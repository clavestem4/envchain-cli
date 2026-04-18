"""Lint chains for common issues with variable names and values."""

import re
from typing import Any

SUSPICIOUS_VALUE_PATTERNS = [
    (r"^(password|secret|token|key)$", "Value looks like a placeholder"),
    (r"^your[-_].*", "Value looks like a placeholder"),
    (r"^<.*>$", "Value is an unfilled template placeholder"),
    (r"^\$\{.*\}$", "Value is an unfilled shell variable"),
]

INVALID_NAME_PATTERN = re.compile(r"^[A-Z_][A-Z0-9_]*$")


def lint_name(name: str) -> list[str]:
    """Return a list of warnings for a variable name."""
    warnings = []
    if not INVALID_NAME_PATTERN.match(name):
        warnings.append(f"'{name}' does not follow UPPER_SNAKE_CASE convention")
    if name.startswith("_"):
        warnings.append(f"'{name}' starts with underscore, which is unusual")
    return warnings


def lint_value(name: str, value: str) -> list[str]:
    """Return a list of warnings for a variable value."""
    warnings = []
    if value == "":
        warnings.append(f"'{name}' has an empty value")
        return warnings
    for pattern, message in SUSPICIOUS_VALUE_PATTERNS:
        if re.match(pattern, value, re.IGNORECASE):
            warnings.append(f"'{name}': {message}")
    return warnings


def lint_chain(chain: dict[str, Any]) -> dict[str, list[str]]:
    """Lint all variables in a chain. Returns a dict of name -> [warnings]."""
    results: dict[str, list[str]] = {}
    for name, value in chain.items():
        issues = lint_name(name) + lint_value(name, value)
        if issues:
            results[name] = issues
    return results
