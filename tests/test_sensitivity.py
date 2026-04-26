import pytest
from unittest.mock import MagicMock
from envchain.sensitivity import (
    set_sensitivity,
    get_sensitivity,
    clear_sensitivity,
    list_by_sensitivity,
    SensitivityError,
)


@pytest.fixture
def mock_chain_fns():
    store = {}

    def fake_get(name, password):
        if name not in store:
            raise KeyError(name)
        return dict(store[name])

    def fake_add(name, password, data):
        store[name] = dict(data)

    def fake_names():
        return list(store.keys())

    store["mychain"] = {"API_KEY": "abc123"}
    store["otherchain"] = {"TOKEN": "xyz"}
    return fake_get, fake_add, fake_names


def test_set_and_get_sensitivity(mock_chain_fns):
    fake_get, fake_add, fake_names = mock_chain_fns
    set_sensitivity("mychain", "confidential", "pass", fake_get, fake_add)
    level = get_sensitivity("mychain", "pass", fake_get)
    assert level == "confidential"


def test_set_sensitivity_invalid_level(mock_chain_fns):
    fake_get, fake_add, _ = mock_chain_fns
    with pytest.raises(SensitivityError, match="Invalid sensitivity level"):
        set_sensitivity("mychain", "ultra-secret", "pass", fake_get, fake_add)


def test_set_sensitivity_missing_chain(mock_chain_fns):
    fake_get, fake_add, _ = mock_chain_fns
    with pytest.raises(SensitivityError, match="not found"):
        set_sensitivity("ghost", "secret", "pass", fake_get, fake_add)


def test_get_sensitivity_unset(mock_chain_fns):
    fake_get, _, _ = mock_chain_fns
    level = get_sensitivity("mychain", "pass", fake_get)
    assert level is None


def test_get_sensitivity_missing_chain(mock_chain_fns):
    fake_get, _, _ = mock_chain_fns
    with pytest.raises(SensitivityError, match="not found"):
        get_sensitivity("ghost", "pass", fake_get)


def test_clear_sensitivity(mock_chain_fns):
    fake_get, fake_add, _ = mock_chain_fns
    set_sensitivity("mychain", "internal", "pass", fake_get, fake_add)
    clear_sensitivity("mychain", "pass", fake_get, fake_add)
    level = get_sensitivity("mychain", "pass", fake_get)
    assert level is None


def test_clear_sensitivity_missing_chain(mock_chain_fns):
    fake_get, fake_add, _ = mock_chain_fns
    with pytest.raises(SensitivityError, match="not found"):
        clear_sensitivity("ghost", "pass", fake_get, fake_add)


def test_list_by_sensitivity(mock_chain_fns):
    fake_get, fake_add, fake_names = mock_chain_fns
    set_sensitivity("mychain", "secret", "pass", fake_get, fake_add)
    set_sensitivity("otherchain", "public", "pass", fake_get, fake_add)
    result = list_by_sensitivity("secret", "pass", fake_names, fake_get)
    assert result == ["mychain"]


def test_list_by_sensitivity_invalid_level(mock_chain_fns):
    fake_get, _, fake_names = mock_chain_fns
    with pytest.raises(SensitivityError, match="Invalid sensitivity level"):
        list_by_sensitivity("unknown", "pass", fake_names, fake_get)


def test_list_by_sensitivity_empty(mock_chain_fns):
    fake_get, _, fake_names = mock_chain_fns
    result = list_by_sensitivity("top-secret", "pass", fake_names, fake_get)
    assert result == []
