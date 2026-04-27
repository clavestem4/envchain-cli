import pytest
from unittest.mock import patch, MagicMock
from envchain.confidence import (
    set_confidence,
    get_confidence,
    clear_confidence,
    list_by_confidence,
    ConfidenceError,
)


@pytest.fixture
def mock_chain_fns():
    store = {}

    def fake_get(name, password):
        if name not in store:
            raise KeyError(f"Chain '{name}' not found")
        return dict(store[name])

    def fake_add(name, data, password):
        store[name] = dict(data)

    def fake_names(password):
        return list(store.keys())

    with patch("envchain.confidence.get_chain", side_effect=fake_get), \
         patch("envchain.confidence.update_chain", side_effect=fake_add), \
         patch("envchain.confidence.get_chain_names", side_effect=fake_names):
        store["mychain"] = {"KEY": "val"}
        store["otherchain"] = {"FOO": "bar", "__confidence__": "high"}
        yield store


def test_set_and_get_confidence(mock_chain_fns):
    set_confidence("mychain", "medium", "pass")
    level = get_confidence("mychain", "pass")
    assert level == "medium"


def test_set_confidence_invalid_level(mock_chain_fns):
    with pytest.raises(ConfidenceError, match="Invalid confidence level"):
        set_confidence("mychain", "extreme", "pass")


def test_get_confidence_unset(mock_chain_fns):
    result = get_confidence("mychain", "pass")
    assert result is None


def test_get_confidence_existing(mock_chain_fns):
    result = get_confidence("otherchain", "pass")
    assert result == "high"


def test_clear_confidence_success(mock_chain_fns):
    clear_confidence("otherchain", "pass")
    result = get_confidence("otherchain", "pass")
    assert result is None


def test_clear_confidence_not_set(mock_chain_fns):
    with pytest.raises(ConfidenceError, match="No confidence level"):
        clear_confidence("mychain", "pass")


def test_list_by_confidence_all(mock_chain_fns):
    result = list_by_confidence("pass")
    assert result == {"otherchain": "high"}


def test_list_by_confidence_filtered(mock_chain_fns):
    set_confidence("mychain", "low", "pass")
    result = list_by_confidence("pass", level="high")
    assert "otherchain" in result
    assert "mychain" not in result


def test_list_by_confidence_no_match(mock_chain_fns):
    result = list_by_confidence("pass", level="verified")
    assert result == {}
