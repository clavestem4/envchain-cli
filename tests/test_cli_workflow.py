import pytest
from click.testing import CliRunner
from unittest.mock import patch
from envchain.cli_workflow import workflow_group
from envchain.workflow import WorkflowError


@pytest.fixture
def runner():
    return CliRunner()


def test_workflow_set_success(runner):
    with patch("envchain.cli_workflow.set_workflow") as mock_set:
        result = runner.invoke(workflow_group, ["set", "deploy", "alpha", "beta"])
        assert result.exit_code == 0
        assert "deploy" in result.output
        mock_set.assert_called_once_with("deploy", ["alpha", "beta"])


def test_workflow_set_missing_chain(runner):
    with patch("envchain.cli_workflow.set_workflow", side_effect=WorkflowError("Chain 'x' does not exist.")):
        result = runner.invoke(workflow_group, ["set", "deploy", "x"])
        assert result.exit_code == 1
        assert "does not exist" in result.output


def test_workflow_get_success(runner):
    with patch("envchain.cli_workflow.get_workflow", return_value=["alpha", "beta"]):
        result = runner.invoke(workflow_group, ["get", "deploy"])
        assert result.exit_code == 0
        assert "alpha" in result.output
        assert "beta" in result.output


def test_workflow_get_missing(runner):
    with patch("envchain.cli_workflow.get_workflow", side_effect=WorkflowError("not found")):
        result = runner.invoke(workflow_group, ["get", "nope"])
        assert result.exit_code == 1


def test_workflow_remove_success(runner):
    with patch("envchain.cli_workflow.remove_workflow") as mock_rm:
        result = runner.invoke(workflow_group, ["remove", "deploy"])
        assert result.exit_code == 0
        assert "removed" in result.output


def test_workflow_list_empty(runner):
    with patch("envchain.cli_workflow.list_workflows", return_value={}):
        result = runner.invoke(workflow_group, ["list"])
        assert "No workflows" in result.output


def test_workflow_list_with_entries(runner):
    with patch("envchain.cli_workflow.list_workflows", return_value={"deploy": ["alpha", "beta"]}):
        result = runner.invoke(workflow_group, ["list"])
        assert "deploy" in result.output
        assert "alpha" in result.output
