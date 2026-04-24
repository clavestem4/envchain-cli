"""Tests for envchain.environment module."""

import pytest
from unittest.mock import patch, MagicMock
from envchain.environment import (
    set_environment,
    get_environment,
    clear_environment,
    list_by_environment,
    EnvironmentError,
    ENV_PROFILE_KEY,
)


@pytest.fixture
def mock_chain_fns():
    store = {}

    def fake_get(name, password):
        if name not in store:
            raise KeyError(name)
        return dict(store[name])

    def fake_add(name, data, password, overwrite=False):
        store[name] = dict(data)

    def fake_names(password):
        return list(store.keys())

    with patch("envchain.environment.get_chain", side_effect=fake_get), \
         patch("envchain.environment.add_chain", side_effect=fake_add), \
         patch("envchain.environment.get_chain_names", side_effect=fake_names):
        store["mychain"] = {"API_KEY": "abc123"}
        store["otherchain"] = {"TOKEN": "xyz", ENV_PROFILE_KEY: "staging"}
        yield store


def test_set_environment_valid(mock_chain_fns):
    set_environment("mychain", "production", "pass")
    assert mock_chain_fns["mychain"][ENV_PROFILE_KEY] == "production"


def test_set_environment_invalid_profile(mock_chain_fns):
    with pytest.raises(EnvironmentError, match="Invalid profile"):
        set_environment("mychain", "chaos", "pass")


def test_set_environment_missing_chain(mock_chain_fns):
    with pytest.raises(EnvironmentError, match="not found"):
        set_environment("ghost", "staging", "pass")


def test_get_environment_returns_profile(mock_chain_fns):
    result = get_environment("otherchain", "pass")
    assert result == "staging"


def test_get_environment_returns_none_when_unset(mock_chain_fns):
    result = get_environment("mychain", "pass")
    assert result is None


def test_get_environment_missing_chain(mock_chain_fns):
    with pytest.raises(EnvironmentError, match="not found"):
        get_environment("ghost", "pass")


def test_clear_environment_removes_key(mock_chain_fns):
    clear_environment("otherchain", "pass")
    assert ENV_PROFILE_KEY not in mock_chain_fns["otherchain"]


def test_clear_environment_missing_chain(mock_chain_fns):
    with pytest.raises(EnvironmentError, match="not found"):
        clear_environment("ghost", "pass")


def test_list_by_environment_returns_matching(mock_chain_fns):
    mock_chain_fns["mychain"][ENV_PROFILE_KEY] = "staging"
    result = list_by_environment("staging", "pass")
    assert set(result) == {"mychain", "otherchain"}


def test_list_by_environment_no_matches(mock_chain_fns):
    result = list_by_environment("production", "pass")
    assert result == []


def test_list_by_environment_invalid_profile(mock_chain_fns):
    with pytest.raises(EnvironmentError, match="Invalid profile"):
        list_by_environment("unknown", "pass")
