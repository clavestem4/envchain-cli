"""Tests for envchain.visibility module."""

import pytest
from unittest.mock import patch, MagicMock
from envchain.visibility import set_visibility, get_visibility, clear_visibility, list_by_visibility, VisibilityError

PASSWORD = "test"


@pytest.fixture
def mock_chain_fns():
    store = {}

    def fake_get(name, pw):
        if name not in store:
            raise KeyError(name)
        return dict(store[name])

    def fake_add(name, data, pw, overwrite=False):
        store[name] = dict(data)

    def fake_names(pw):
        return list(store.keys())

    with patch("envchain.visibility.get_chain", side_effect=fake_get), \
         patch("envchain.visibility.add_chain", side_effect=fake_add), \
         patch("envchain.visibility.get_chain_names", side_effect=fake_names):
        store["alpha"] = {"KEY": "val"}
        store["beta"] = {"KEY": "val", "__visibility__": "public"}
        store["gamma"] = {"KEY": "val", "__visibility__": "shared"}
        yield store


def test_set_visibility_valid(mock_chain_fns):
    set_visibility("alpha", "public", PASSWORD)
    assert mock_chain_fns["alpha"]["__visibility__"] == "public"


def test_set_visibility_invalid_level(mock_chain_fns):
    with pytest.raises(VisibilityError, match="Invalid visibility"):
        set_visibility("alpha", "secret", PASSWORD)


def test_get_visibility_explicit(mock_chain_fns):
    assert get_visibility("beta", PASSWORD) == "public"


def test_get_visibility_default(mock_chain_fns):
    assert get_visibility("alpha", PASSWORD) == "private"


def test_clear_visibility(mock_chain_fns):
    clear_visibility("beta", PASSWORD)
    assert "__visibility__" not in mock_chain_fns["beta"]


def test_list_by_visibility_public(mock_chain_fns):
    result = list_by_visibility("public", PASSWORD)
    assert "beta" in result
    assert "alpha" not in result


def test_list_by_visibility_private(mock_chain_fns):
    result = list_by_visibility("private", PASSWORD)
    assert "alpha" in result


def test_list_by_visibility_invalid(mock_chain_fns):
    with pytest.raises(VisibilityError):
        list_by_visibility("hidden", PASSWORD)
