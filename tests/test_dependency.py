"""Tests for envchain.dependency module."""

import pytest
from unittest.mock import patch
from envchain.dependency import (
    set_dependencies, get_dependencies, clear_dependencies, resolve_order, DependencyError
)

CHAINS = {
    "app": {"DB_URL": "postgres://", "__meta__": {}},
    "db": {"DB_PASS": "secret", "__meta__": {}},
    "cache": {"REDIS_URL": "redis://", "__meta__": {}},
}


@pytest.fixture
def mock_fns():
    store = {k: dict(v) for k, v in CHAINS.items()}

    def fake_get(name, pw):
        if name not in store:
            raise KeyError(name)
        return dict(store[name])

    def fake_add(name, chain, pw, overwrite=False):
        store[name] = dict(chain)

    def fake_names(pw):
        return list(store.keys())

    with patch("envchain.dependency.get_chain", side_effect=fake_get), \
         patch("envchain.dependency.add_chain", side_effect=fake_add), \
         patch("envchain.dependency.get_chain_names", side_effect=fake_names):
        yield store


def test_set_and_get_dependencies(mock_fns):
    set_dependencies("app", ["db"], "pw")
    assert get_dependencies("app", "pw") == ["db"]


def test_set_dependency_missing_chain(mock_fns):
    with pytest.raises(DependencyError, match="does not exist"):
        set_dependencies("app", ["missing"], "pw")


def test_set_self_dependency_raises(mock_fns):
    with pytest.raises(DependencyError, match="cannot depend on itself"):
        set_dependencies("app", ["app"], "pw")


def test_clear_dependencies(mock_fns):
    set_dependencies("app", ["db"], "pw")
    clear_dependencies("app", "pw")
    assert get_dependencies("app", "pw") == []


def test_resolve_order_no_deps(mock_fns):
    order = resolve_order(["app", "db"], "pw")
    assert set(order) == {"app", "db"}


def test_resolve_order_with_deps(mock_fns):
    set_dependencies("app", ["db"], "pw")
    order = resolve_order(["app", "db"], "pw")
    assert order.index("db") < order.index("app")


def test_resolve_order_circular_raises(mock_fns):
    set_dependencies("app", ["db"], "pw")
    set_dependencies("db", ["app"], "pw")
    with pytest.raises(DependencyError, match="Circular"):
        resolve_order(["app", "db"], "pw")


def test_get_dependencies_none_set(mock_fns):
    assert get_dependencies("cache", "pw") == []
