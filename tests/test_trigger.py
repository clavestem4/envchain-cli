"""Tests for envchain.trigger module."""

import pytest
from unittest.mock import patch, MagicMock
from envchain.trigger import (
    set_trigger,
    get_trigger,
    remove_trigger,
    list_triggers,
    find_chains_with_trigger,
    TriggerError,
)


@pytest.fixture
def mock_chain_fns():
    store = {}

    def fake_get(name):
        if name not in store:
            raise KeyError(name)
        return dict(store[name])

    def fake_add(name, data, overwrite=False):
        store[name] = dict(data)

    def fake_names():
        return list(store.keys())

    with patch("envchain.trigger.get_chain", side_effect=fake_get), \
         patch("envchain.trigger.add_chain", side_effect=fake_add), \
         patch("envchain.trigger.get_chain_names", side_effect=fake_names):
        store["mychain"] = {"FOO": "bar"}
        yield store


def test_set_trigger_success(mock_chain_fns):
    set_trigger("mychain", "on_get", "echo accessed")
    chain = mock_chain_fns["mychain"]
    assert chain["__triggers__"]["on_get"] == "echo accessed"


def test_set_trigger_invalid_event(mock_chain_fns):
    with pytest.raises(TriggerError, match="Invalid event"):
        set_trigger("mychain", "on_fly", "echo nope")


def test_get_trigger_returns_command(mock_chain_fns):
    set_trigger("mychain", "on_set", "notify-send updated")
    cmd = get_trigger("mychain", "on_set")
    assert cmd == "notify-send updated"


def test_get_trigger_returns_none_if_unset(mock_chain_fns):
    assert get_trigger("mychain", "on_delete") is None


def test_get_trigger_invalid_event(mock_chain_fns):
    with pytest.raises(TriggerError):
        get_trigger("mychain", "on_fly")


def test_remove_trigger_success(mock_chain_fns):
    set_trigger("mychain", "on_get", "echo hi")
    remove_trigger("mychain", "on_get")
    assert get_trigger("mychain", "on_get") is None


def test_remove_trigger_not_set_raises(mock_chain_fns):
    with pytest.raises(TriggerError, match="No trigger set"):
        remove_trigger("mychain", "on_get")


def test_list_triggers_empty(mock_chain_fns):
    assert list_triggers("mychain") == {}


def test_list_triggers_multiple(mock_chain_fns):
    set_trigger("mychain", "on_get", "echo get")
    set_trigger("mychain", "on_set", "echo set")
    result = list_triggers("mychain")
    assert result == {"on_get": "echo get", "on_set": "echo set"}


def test_find_chains_with_trigger(mock_chain_fns):
    mock_chain_fns["other"] = {"X": "1"}
    set_trigger("mychain", "on_delete", "rm -rf /tmp/cache")
    found = find_chains_with_trigger("on_delete")
    assert "mychain" in found
    assert "other" not in found


def test_find_chains_invalid_event(mock_chain_fns):
    with pytest.raises(TriggerError):
        find_chains_with_trigger("on_fly")
