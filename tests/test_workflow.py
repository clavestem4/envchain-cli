import pytest
from unittest.mock import MagicMock
from envchain.workflow import set_workflow, get_workflow, remove_workflow, list_workflows, WorkflowError


@pytest.fixture
def mock_fns():
    store = {}

    def fake_get(name):
        if name not in store:
            raise KeyError(name)
        return store[name]

    def fake_add(name, data, overwrite=False):
        store[name] = data

    def fake_names():
        return list(store.keys())

    return fake_get, fake_add, fake_names, store


def test_set_and_get_workflow(mock_fns):
    fake_get, fake_add, fake_names, store = mock_fns
    fake_add("alpha", {"A": "1"})
    fake_add("beta", {"B": "2"})
    set_workflow("deploy", ["alpha", "beta"], fake_get, fake_names, fake_add)
    result = get_workflow("deploy", fake_get, fake_names)
    assert result == ["alpha", "beta"]


def test_set_workflow_missing_chain(mock_fns):
    fake_get, fake_add, fake_names, store = mock_fns
    with pytest.raises(WorkflowError, match="does not exist"):
        set_workflow("deploy", ["missing"], fake_get, fake_names, fake_add)


def test_get_workflow_missing(mock_fns):
    fake_get, fake_add, fake_names, store = mock_fns
    with pytest.raises(WorkflowError, match="not found"):
        get_workflow("nope", fake_get, fake_names)


def test_remove_workflow(mock_fns):
    fake_get, fake_add, fake_names, store = mock_fns
    fake_add("alpha", {"A": "1"})
    set_workflow("deploy", ["alpha"], fake_get, fake_names, fake_add)
    remove_workflow("deploy", fake_get, fake_names, fake_add)
    with pytest.raises(WorkflowError):
        get_workflow("deploy", fake_get, fake_names)


def test_remove_workflow_missing(mock_fns):
    fake_get, fake_add, fake_names, store = mock_fns
    with pytest.raises(WorkflowError, match="not found"):
        remove_workflow("nope", fake_get, fake_names, fake_add)


def test_list_workflows(mock_fns):
    fake_get, fake_add, fake_names, store = mock_fns
    fake_add("alpha", {"A": "1"})
    fake_add("beta", {"B": "2"})
    set_workflow("deploy", ["alpha"], fake_get, fake_names, fake_add)
    set_workflow("test", ["beta"], fake_get, fake_names, fake_add)
    result = list_workflows(fake_get, fake_names)
    assert "deploy" in result
    assert "test" in result


def test_list_workflows_empty(mock_fns):
    fake_get, fake_add, fake_names, store = mock_fns
    result = list_workflows(fake_get, fake_names)
    assert result == {}
