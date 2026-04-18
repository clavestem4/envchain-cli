"""Tests for envchain.notes."""
import pytest
from unittest.mock import patch, MagicMock
from envchain.notes import set_note, get_note, clear_note, _NOTES_KEY


@pytest.fixture
def mock_chain_fns():
    store = {}

    def fake_get(name, password):
        if name not in store:
            raise KeyError(name)
        return dict(store[name])

    def fake_add(name, data, password, overwrite=False):
        store[name] = dict(data)

    with patch("envchain.notes.get_chain", side_effect=fake_get), \
         patch("envchain.notes.add_chain", side_effect=fake_add):
        store["mychain"] = {"FOO": "bar"}
        yield store


def test_set_note(mock_chain_fns):
    set_note("mychain", "This is a test chain", "pass")
    assert mock_chain_fns["mychain"][_NOTES_KEY] == "This is a test chain"


def test_set_note_preserves_existing_vars(mock_chain_fns):
    """Setting a note should not remove other env vars in the chain."""
    set_note("mychain", "my note", "pass")
    assert mock_chain_fns["mychain"]["FOO"] == "bar"
    assert mock_chain_fns["mychain"][_NOTES_KEY] == "my note"


def test_get_note(mock_chain_fns):
    mock_chain_fns["mychain"][_NOTES_KEY] = "hello"
    result = get_note("mychain", "pass")
    assert result == "hello"


def test_get_note_empty(mock_chain_fns):
    result = get_note("mychain", "pass")
    assert result == ""


def test_clear_note(mock_chain_fns):
    mock_chain_fns["mychain"][_NOTES_KEY] = "to be removed"
    clear_note("mychain", "pass")
    assert _NOTES_KEY not in mock_chain_fns["mychain"]


def test_clear_note_preserves_existing_vars(mock_chain_fns):
    """Clearing a note should not remove other env vars in the chain."""
    mock_chain_fns["mychain"][_NOTES_KEY] = "to be removed"
    clear_note("mychain", "pass")
    assert mock_chain_fns["mychain"]["FOO"] == "bar"


def test_set_note_missing_chain(mock_chain_fns):
    with pytest.raises(KeyError):
        set_note("ghost", "note", "pass")


def test_get_note_missing_chain(mock_chain_fns):
    with pytest.raises(KeyError):
        get_note("ghost", "pass")


def test_clear_note_missing_chain(mock_chain_fns):
    with pytest.raises(KeyError):
        clear_note("ghost", "pass")
