"""Tests for envchain.priority module."""

import pytest
from unittest.mock import patch, MagicMock
from envchain import priority as P
from envchain.priority import PriorityError


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

    with patch.object(P, "get_chain", side_effect=fake_get), \
         patch.object(P, "add_chain", side_effect=fake_add), \
         patch.object(P, "get_chain_names", side_effect=fake_names):
        store["alpha"] = {"FOO": "bar"}
        store["beta"] = {"X": "1"}
        yield store


def test_set_and_get_priority(mock_chain_fns):
    P.set_priority("alpha", 5, "pw")
    assert P.get_priority("alpha", "pw") == 5


def test_get_priority_unset(mock_chain_fns):
    assert P.get_priority("alpha", "pw") is None


def test_clear_priority(mock_chain_fns):
    P.set_priority("alpha", 3, "pw")
    P.clear_priority("alpha", "pw")
    assert P.get_priority("alpha", "pw") is None


def test_clear_priority_not_set_raises(mock_chain_fns):
    with pytest.raises(PriorityError):
        P.clear_priority("alpha", "pw")


def test_list_by_priority_sorted(mock_chain_fns):
    P.set_priority("beta", 10, "pw")
    P.set_priority("alpha", 1, "pw")
    result = P.list_by_priority("pw")
    names = [r[0] for r in result]
    assert names.index("alpha") < names.index("beta")


def test_list_by_priority_unset_last(mock_chain_fns):
    P.set_priority("beta", 2, "pw")
    result = P.list_by_priority("pw")
    names = [r[0] for r in result]
    assert names[-1] == "alpha"


def test_set_priority_preserves_vars(mock_chain_fns):
    P.set_priority("alpha", 7, "pw")
    chain = mock_chain_fns["alpha"]
    assert chain["FOO"] == "bar"
    assert chain[P.PRIORITY_KEY] == "7"
