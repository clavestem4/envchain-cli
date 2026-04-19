"""Tests for envchain.rating module."""

import pytest
from unittest.mock import patch, MagicMock
from envchain.rating import set_rating, get_rating, clear_rating, list_by_rating, RatingError

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

    with patch("envchain.rating.get_chain", side_effect=fake_get), \
         patch("envchain.rating.add_chain", side_effect=fake_add), \
         patch("envchain.rating.get_chain_names", side_effect=fake_names):
        store["mychain"] = {"KEY": "val"}
        yield store


def test_set_and_get_rating(mock_chain_fns):
    set_rating("mychain", 4, PASSWORD)
    assert get_rating("mychain", PASSWORD) == 4


def test_set_invalid_rating(mock_chain_fns):
    with pytest.raises(RatingError):
        set_rating("mychain", 6, PASSWORD)


def test_set_zero_rating(mock_chain_fns):
    with pytest.raises(RatingError):
        set_rating("mychain", 0, PASSWORD)


def test_get_unset_rating(mock_chain_fns):
    assert get_rating("mychain", PASSWORD) is None


def test_clear_rating(mock_chain_fns):
    set_rating("mychain", 3, PASSWORD)
    clear_rating("mychain", PASSWORD)
    assert get_rating("mychain", PASSWORD) is None


def test_clear_unset_rating_raises(mock_chain_fns):
    with pytest.raises(RatingError):
        clear_rating("mychain", PASSWORD)


def test_list_by_rating(mock_chain_fns):
    mock_chain_fns["chain_a"] = {"X": "1"}
    mock_chain_fns["chain_b"] = {"Y": "2"}
    set_rating("mychain", 5, PASSWORD)
    set_rating("chain_a", 2, PASSWORD)
    set_rating("chain_b", 4, PASSWORD)
    results = list_by_rating(PASSWORD)
    assert results[0] == ("mychain", 5)
    assert results[1] == ("chain_b", 4)
    assert results[2] == ("chain_a", 2)


def test_list_by_rating_min_filter(mock_chain_fns):
    mock_chain_fns["chain_a"] = {"X": "1"}
    set_rating("mychain", 5, PASSWORD)
    set_rating("chain_a", 2, PASSWORD)
    results = list_by_rating(PASSWORD, min_rating=3)
    names = [r[0] for r in results]
    assert "mychain" in names
    assert "chain_a" not in names
