import pytest
from unittest.mock import MagicMock
from envchain.env_group import create_group, get_group, delete_group, list_groups, GroupError


def _make_fns(initial=None):
    store = {"__meta__": initial or {}}

    def fake_get(name):
        if name not in store:
            raise KeyError(name)
        return store[name]

    def fake_add(name, data):
        store[name] = data

    return fake_get, fake_add, store


def test_create_group_success(monkeypatch):
    fake_get, fake_add, store = _make_fns()
    monkeypatch.setattr("envchain.env_group.get_chain_names", lambda: ["dev", "prod"])
    create_group("mygroup", ["dev", "prod"], fake_get, fake_add)
    assert store["__meta__"]["__groups__"]["mygroup"] == ["dev", "prod"]


def test_create_group_missing_chain(monkeypatch):
    fake_get, fake_add, _ = _make_fns()
    monkeypatch.setattr("envchain.env_group.get_chain_names", lambda: ["dev"])
    with pytest.raises(GroupError, match="prod"):
        create_group("mygroup", ["dev", "prod"], fake_get, fake_add)


def test_get_group_success(monkeypatch):
    fake_get, fake_add, _ = _make_fns({"__groups__": {"g1": ["a", "b"]}})
    result = get_group("g1", fake_get)
    assert result == ["a", "b"]


def test_get_group_missing(monkeypatch):
    fake_get, _, _ = _make_fns({})
    with pytest.raises(GroupError, match="not found"):
        get_group("nope", fake_get)


def test_delete_group_success(monkeypatch):
    fake_get, fake_add, store = _make_fns({"__groups__": {"g1": ["x"]}})
    delete_group("g1", fake_get, fake_add)
    assert "g1" not in store["__meta__"]["__groups__"]


def test_delete_group_missing():
    fake_get, fake_add, _ = _make_fns({})
    with pytest.raises(GroupError):
        delete_group("ghost", fake_get, fake_add)


def test_list_groups_empty():
    def fake_get(name):
        raise KeyError(name)
    result = list_groups(fake_get)
    assert result == {}


def test_list_groups_returns_all():
    fake_get, _, _ = _make_fns({"__groups__": {"g1": ["a"], "g2": ["b", "c"]}})
    result = list_groups(fake_get)
    assert "g1" in result
    assert "g2" in result
