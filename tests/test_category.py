import pytest
from unittest.mock import patch, MagicMock
from envchain.category import (
    set_category, get_category, clear_category,
    list_by_category, list_all_categories, CategoryError
)

PASSWORD = "test"


@pytest.fixture
def mock_chain_fns():
    store = {}

    def fake_get(name, pw):
        return dict(store[name]) if name in store else None

    def fake_add(name, data, pw, overwrite=False):
        store[name] = dict(data)

    def fake_names(pw):
        return list(store.keys())

    with patch("envchain.category.get_chain", side_effect=fake_get), \
         patch("envchain.category.add_chain", side_effect=fake_add), \
         patch("envchain.category.get_chain_names", side_effect=fake_names):
        yield store


def test_set_category_success(mock_chain_fns):
    mock_chain_fns["mychain"] = {"VAR": "val"}
    set_category("mychain", "production", PASSWORD)
    assert mock_chain_fns["mychain"]["__category__"] == "production"


def test_set_category_missing_chain(mock_chain_fns):
    with pytest.raises(CategoryError, match="not found"):
        set_category("ghost", "dev", PASSWORD)


def test_get_category_value(mock_chain_fns):
    mock_chain_fns["mychain"] = {"VAR": "val", "__category__": "staging"}
    assert get_category("mychain", PASSWORD) == "staging"


def test_get_category_unset(mock_chain_fns):
    mock_chain_fns["mychain"] = {"VAR": "val"}
    assert get_category("mychain", PASSWORD) is None


def test_clear_category(mock_chain_fns):
    mock_chain_fns["mychain"] = {"VAR": "val", "__category__": "prod"}
    clear_category("mychain", PASSWORD)
    assert "__category__" not in mock_chain_fns["mychain"]


def test_list_by_category(mock_chain_fns):
    mock_chain_fns["a"] = {"__category__": "prod"}
    mock_chain_fns["b"] = {"__category__": "dev"}
    mock_chain_fns["c"] = {"__category__": "prod"}
    result = list_by_category("prod", PASSWORD)
    assert sorted(result) == ["a", "c"]


def test_list_all_categories(mock_chain_fns):
    mock_chain_fns["a"] = {"__category__": "prod"}
    mock_chain_fns["b"] = {"__category__": "dev"}
    mock_chain_fns["c"] = {"__category__": "prod"}
    mock_chain_fns["d"] = {"VAR": "no_cat"}
    cats = list_all_categories(PASSWORD)
    assert sorted(cats["prod"]) == ["a", "c"]
    assert cats["dev"] == ["b"]
    assert "d" not in cats.get("prod", []) + cats.get("dev", [])
