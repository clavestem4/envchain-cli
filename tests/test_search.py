"""Tests for envchain.search module."""
import pytest
from unittest.mock import patch
from envchain.search import search_chains, search_variables, search_all

MOCK_CHAINS = {
    "myproject": {"DATABASE_URL": "postgres://...", "SECRET_KEY": "abc"},
    "staging-api": {"API_KEY": "xyz", "DATABASE_URL": "mysql://..."},
    "frontend": {"NODE_ENV": "production", "PORT": "3000"},
}


def _mock_get_chain_names(password, **kwargs):
    return list(MOCK_CHAINS.keys())


def _mock_get_chain(name, password, **kwargs):
    if name not in MOCK_CHAINS:
        raise KeyError(name)
    return MOCK_CHAINS[name]


@pytest.fixture(autouse=True)
def mock_chain_fns():
    with patch("envchain.search.get_chain_names", side_effect=_mock_get_chain_names), \
         patch("envchain.search.get_chain", side_effect=_mock_get_chain):
        yield


def test_search_chains_by_name():
    results = search_chains("pass", "project")
    assert len(results) == 1
    assert results[0]["chain"] == "myproject"
    assert results[0]["match"] == "name"


def test_search_chains_no_match():
    results = search_chains("pass", "zzznomatch")
    assert results == []


def test_search_chains_multiple_matches():
    results = search_chains("pass", "a")
    chains = [r["chain"] for r in results]
    assert "staging-api" in chains
    assert "myproject" in chains


def test_search_variables_by_key():
    results = search_variables("pass", "DATABASE_URL")
    assert len(results) == 2
    chains = [r["chain"] for r in results]
    assert "myproject" in chains
    assert "staging-api" in chains
    for r in results:
        assert r["match"] == "variable"


def test_search_variables_no_match():
    results = search_variables("pass", "NONEXISTENT_VAR")
    assert results == []


def test_search_variables_partial_key():
    results = search_variables("pass", "key")
    chains = [r["chain"] for r in results]
    assert "myproject" in chains  # SECRET_KEY
    assert "staging-api" in chains  # API_KEY


def test_search_all_name_and_variable():
    # 'api' matches chain 'staging-api' by name and API_KEY by variable
    results = search_all("pass", "api")
    staging = next((r for r in results if r["chain"] == "staging-api"), None)
    assert staging is not None
    assert staging["match"] == "both"


def test_search_all_only_name():
    results = search_all("pass", "frontend")
    assert len(results) == 1
    assert results[0]["match"] == "name"


def test_search_all_only_variable():
    results = search_all("pass", "NODE_ENV")
    assert len(results) == 1
    assert results[0]["chain"] == "frontend"
    assert results[0]["match"] == "variable"


def test_search_all_returns_each_chain_once():
    """Ensure search_all never returns duplicate entries for the same chain."""
    results = search_all("pass", "api")
    chain_names = [r["chain"] for r in results]
    assert len(chain_names) == len(set(chain_names)), "Duplicate chain entries found in search_all results"
