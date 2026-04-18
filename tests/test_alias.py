import pytest
from envchain.alias import set_alias, remove_alias, resolve_alias, list_aliases


@pytest.fixture
def mock_fns():
    store = {}

    def fake_get(name, password):
        return store.get(name, {"vars": {}})

    def fake_add(name, password, variables, overwrite=False):
        store[name] = {"vars": variables}

    def fake_names():
        return list(store.keys())

    store["prod"] = {"vars": {"KEY": "val"}}
    store["staging"] = {"vars": {"KEY": "val2"}}
    return fake_get, fake_add, fake_names


def test_set_alias(mock_fns):
    get, add, names = mock_fns
    set_alias("p", "prod", get, add, names)
    aliases = list_aliases(get, names)
    assert aliases["p"] == "prod"


def test_set_alias_missing_target(mock_fns):
    get, add, names = mock_fns
    with pytest.raises(KeyError, match="does not exist"):
        set_alias("x", "nonexistent", get, add, names)


def test_remove_alias(mock_fns):
    get, add, names = mock_fns
    set_alias("p", "prod", get, add, names)
    remove_alias("p", get, add, names)
    aliases = list_aliases(get, names)
    assert "p" not in aliases


def test_remove_alias_missing(mock_fns):
    get, add, names = mock_fns
    with pytest.raises(KeyError, match="does not exist"):
        remove_alias("ghost", get, add, names)


def test_resolve_alias(mock_fns):
    get, add, names = mock_fns
    set_alias("s", "staging", get, add, names)
    assert resolve_alias("s", get, names) == "staging"


def test_resolve_non_alias(mock_fns):
    get, _, names = mock_fns
    assert resolve_alias("prod", get, names) == "prod"


def test_list_aliases_empty(mock_fns):
    get, _, names = mock_fns
    assert list_aliases(get, names) == {}


def test_list_aliases_multiple(mock_fns):
    get, add, names = mock_fns
    set_alias("p", "prod", get, add, names)
    set_alias("s", "staging", get, add, names)
    aliases = list_aliases(get, names)
    assert aliases == {"p": "prod", "s": "staging"}
