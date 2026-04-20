"""Tests for envchain.namespace."""

import pytest
from unittest.mock import patch

from envchain.namespace import (
    qualify,
    split_qualified,
    list_in_namespace,
    get_namespaces,
    get_chains_in_namespace,
    NamespaceError,
)


# ---------------------------------------------------------------------------
# qualify / split helpers
# ---------------------------------------------------------------------------

def test_qualify_basic():
    assert qualify("prod", "api") == "prod.api"


def test_qualify_invalid_namespace_empty():
    with pytest.raises(NamespaceError):
        qualify("", "api")


def test_qualify_invalid_namespace_with_dot():
    with pytest.raises(NamespaceError):
        qualify("prod.staging", "api")


def test_split_qualified_with_namespace():
    ns, name = split_qualified("prod.api")
    assert ns == "prod"
    assert name == "api"


def test_split_qualified_no_namespace():
    ns, name = split_qualified("standalone")
    assert ns is None
    assert name == "standalone"


# ---------------------------------------------------------------------------
# list_in_namespace
# ---------------------------------------------------------------------------

ALL_NAMES = ["prod.api", "prod.db", "staging.api", "standalone"]


@patch("envchain.namespace.get_chain_names", return_value=ALL_NAMES)
def test_list_in_namespace(mock_names):
    result = list_in_namespace("prod", "secret")
    assert result == ["prod.api", "prod.db"]


@patch("envchain.namespace.get_chain_names", return_value=ALL_NAMES)
def test_list_in_namespace_no_match(mock_names):
    result = list_in_namespace("dev", "secret")
    assert result == []


# ---------------------------------------------------------------------------
# get_namespaces
# ---------------------------------------------------------------------------

@patch("envchain.namespace.get_chain_names", return_value=ALL_NAMES)
def test_get_namespaces(mock_names):
    result = get_namespaces("secret")
    assert result == ["prod", "staging"]


@patch("envchain.namespace.get_chain_names", return_value=["standalone"])
def test_get_namespaces_none(mock_names):
    result = get_namespaces("secret")
    assert result == []


# ---------------------------------------------------------------------------
# get_chains_in_namespace
# ---------------------------------------------------------------------------

@patch("envchain.namespace.get_chain_names", return_value=ALL_NAMES)
@patch(
    "envchain.namespace.get_chain",
    side_effect=lambda name, pw: {"KEY": "val_" + name.split(".")[-1]},
)
def test_get_chains_in_namespace(mock_get, mock_names):
    result = get_chains_in_namespace("prod", "secret")
    assert set(result.keys()) == {"api", "db"}
    assert result["api"] == {"KEY": "val_api"}
    assert result["db"] == {"KEY": "val_db"}
