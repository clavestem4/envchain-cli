import pytest
from unittest.mock import MagicMock
from envchain.badge import set_badge, remove_badge, get_badges, find_by_badge, BadgeError


@pytest.fixture
def mock_chain_fns(monkeypatch):
    store = {}

    def fake_get(name, password):
        if name not in store:
            raise KeyError(f"Chain '{name}' not found")
        return dict(store[name])

    def fake_add(name, data, password, overwrite=False):
        store[name] = dict(data)

    def fake_names():
        return list(store.keys())

    monkeypatch.setattr("envchain.badge.get_chain", fake_get)
    monkeypatch.setattr("envchain.badge.add_chain", fake_add)
    store["mychain"] = {"KEY": "val"}
    return store, fake_get, fake_add, fake_names


def test_set_badge_success(mock_chain_fns):
    store, get, add, names = mock_chain_fns
    set_badge("mychain", "stable", "pass")
    assert "stable" in store["mychain"]["__meta__"]["badges"]


def test_set_badge_with_note(mock_chain_fns):
    store, get, add, names = mock_chain_fns
    set_badge("mychain", "wip", "pass", note="needs review")
    assert store["mychain"]["__meta__"]["badges"]["wip"] == "needs review"


def test_set_badge_invalid(mock_chain_fns):
    with pytest.raises(BadgeError, match="Invalid badge"):
        set_badge("mychain", "unknown", "pass")


def test_remove_badge_success(mock_chain_fns):
    store, get, add, names = mock_chain_fns
    set_badge("mychain", "deprecated", "pass")
    remove_badge("mychain", "deprecated", "pass")
    assert "deprecated" not in store["mychain"].get("__meta__", {}).get("badges", {})


def test_remove_badge_not_set(mock_chain_fns):
    with pytest.raises(BadgeError, match="not set"):
        remove_badge("mychain", "stable", "pass")


def test_get_badges_empty(mock_chain_fns):
    result = get_badges("mychain", "pass")
    assert result == {}


def test_get_badges_multiple(mock_chain_fns):
    set_badge("mychain", "stable", "pass")
    set_badge("mychain", "reviewed", "pass", note="ok")
    badges = get_badges("mychain", "pass")
    assert "stable" in badges
    assert badges["reviewed"] == "ok"


def test_find_by_badge(mock_chain_fns):
    store, get, add, names = mock_chain_fns
    store["other"] = {"X": "1"}
    set_badge("mychain", "experimental", "pass")
    results = find_by_badge("experimental", "pass", get_chain_names_fn=names, get_chain_fn=get)
    assert "mychain" in results
    assert "other" not in results


def test_find_by_badge_none(mock_chain_fns):
    store, get, add, names = mock_chain_fns
    results = find_by_badge("broken", "pass", get_chain_names_fn=names, get_chain_fn=get)
    assert results == []
