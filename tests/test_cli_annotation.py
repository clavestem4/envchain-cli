"""Tests for envchain/cli_annotation.py"""

import pytest
from click.testing import CliRunner
from unittest.mock import patch
from envchain.cli_annotation import annotation_group
from envchain.annotation import AnnotationError


@pytest.fixture
def runner():
    return CliRunner()


def test_annotation_set_success(runner):
    with patch("envchain.cli_annotation.set_annotation") as mock_set:
        result = runner.invoke(
            annotation_group,
            ["set", "mychain", "owner", "alice", "--password", "secret"],
        )
        assert result.exit_code == 0
        assert "set" in result.output
        mock_set.assert_called_once_with("mychain", "owner", "alice", "secret")


def test_annotation_set_missing_chain(runner):
    with patch("envchain.cli_annotation.set_annotation", side_effect=KeyError("mychain")):
        result = runner.invoke(
            annotation_group,
            ["set", "mychain", "owner", "alice", "--password", "secret"],
        )
        assert result.exit_code == 1
        assert "not found" in result.output


def test_annotation_remove_success(runner):
    with patch("envchain.cli_annotation.remove_annotation") as mock_rm:
        result = runner.invoke(
            annotation_group,
            ["remove", "mychain", "owner", "--password", "secret"],
        )
        assert result.exit_code == 0
        assert "removed" in result.output


def test_annotation_remove_missing_key(runner):
    with patch(
        "envchain.cli_annotation.remove_annotation",
        side_effect=AnnotationError("Annotation 'owner' not found on chain 'mychain'."),
    ):
        result = runner.invoke(
            annotation_group,
            ["remove", "mychain", "owner", "--password", "secret"],
        )
        assert result.exit_code == 1
        assert "Error" in result.output


def test_annotation_list_with_entries(runner):
    with patch(
        "envchain.cli_annotation.get_annotations",
        return_value={"owner": "alice", "team": "platform"},
    ):
        result = runner.invoke(
            annotation_group,
            ["list", "mychain", "--password", "secret"],
        )
        assert result.exit_code == 0
        assert "owner=alice" in result.output
        assert "team=platform" in result.output


def test_annotation_list_empty(runner):
    with patch("envchain.cli_annotation.get_annotations", return_value={}):
        result = runner.invoke(
            annotation_group,
            ["list", "mychain", "--password", "secret"],
        )
        assert result.exit_code == 0
        assert "No annotations" in result.output


def test_annotation_find_results(runner):
    with patch(
        "envchain.cli_annotation.find_by_annotation",
        return_value=["chain_a", "chain_b"],
    ):
        result = runner.invoke(
            annotation_group,
            ["find", "env", "--password", "secret"],
        )
        assert result.exit_code == 0
        assert "chain_a" in result.output
        assert "chain_b" in result.output


def test_annotation_find_no_results(runner):
    with patch("envchain.cli_annotation.find_by_annotation", return_value=[]):
        result = runner.invoke(
            annotation_group,
            ["find", "env", "--password", "secret"],
        )
        assert result.exit_code == 0
        assert "No chains found" in result.output
