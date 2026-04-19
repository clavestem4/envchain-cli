"""Tests for envchain.version module."""

import pytest
from unittest.mock import patch, MagicMock
from envchain.version import stamp_chain, get_version_info, list_versioned_chains, VersionError


@pytest.fixture
def mock_fns():
    store = {}

    def fake_get(name, password):
        if name not in store:
            raise KeyError(f"Missing: {name}")
        return dict(store[name])

    def fake_add(name, data, password, overwrite=False):
        store[name] = dict(data)

    def fake_names(password):
        return list(store.keys())

    with patch("envchain.version.get_chain", side_effect=fake_get), \
         patch("envchain.version.add_chain", side_effect=fake_add), \
         patch("envchain.version.get_chain_names", side_effect=fake_names):
        yield store


def test_stamp_chain_initial(mock_fns):
    mock_fns["mychain"] = {"FOO": "bar"}
    stamp_chain("mychain", "pass")
    assert mock_fns["mychain"]["__version__"] == "1"
    assert "__created_at__" in mock_fns["mychain"]
    assert "__updated_at__" in mock_fns["mychain"]


def test_stamp_chain_increments(mock_fns):
    mock_fns["mychain"] = {"FOO": "bar"}
    stamp_chain("mychain", "pass")
    stamp_chain("mychain", "pass")
    assert mock_fns["mychain"]["__version__"] == "2"


def test_stamp_chain_missing_raises(mock_fns):
    with pytest.raises(VersionError):
        stamp_chain("ghost", "pass")


def test_get_version_info_unversioned(mock_fns):
    mock_fns["plain"] = {"X": "1"}
    info = get_version_info("plain", "pass")
    assert info["version"] is None
    assert info["created_at"] is None


def test_get_version_info_stamped(mock_fns):
    mock_fns["stamped"] = {"A": "b"}
    stamp_chain("stamped", "pass")
    info = get_version_info("stamped", "pass")
    assert info["version"] == "1"
    assert info["chain"] == "stamped"


def test_list_versioned_chains(mock_fns):
    mock_fns["v1"] = {"__version__": "1", "__created_at__": "x", "__updated_at__": "y"}
    mock_fns["plain"] = {"FOO": "bar"}
    result = list_versioned_chains("pass")
    assert "v1" in result
    assert "plain" not in result


def test_list_versioned_chains_empty(mock_fns):
    mock_fns["a"] = {"K": "v"}
    result = list_versioned_chains("pass")
    assert result == []
