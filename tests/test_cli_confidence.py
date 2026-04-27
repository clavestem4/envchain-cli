import pytest
from click.testing import CliRunner
from unittest.mock import patch
from envchain.cli_confidence import confidence_group
from envchain.confidence import ConfidenceError


@pytest.fixture
def runner():
    return CliRunner()


def test_confidence_set_success(runner):
    with patch("envchain.cli_confidence.set_confidence") as mock_set:
        result = runner.invoke(
            confidence_group, ["set", "mychain", "high", "--password", "secret"]
        )
        mock_set.assert_called_once_with("mychain", "high", "secret")
        assert result.exit_code == 0
        assert "high" in result.output


def test_confidence_set_invalid_level(runner):
    result = runner.invoke(
        confidence_group, ["set", "mychain", "extreme", "--password", "secret"]
    )
    assert result.exit_code != 0


def test_confidence_set_missing_chain(runner):
    with patch(
        "envchain.cli_confidence.set_confidence",
        side_effect=ConfidenceError("chain not found"),
    ):
        result = runner.invoke(
            confidence_group, ["set", "ghost", "low", "--password", "secret"]
        )
        assert result.exit_code == 1
        assert "Error" in result.output


def test_confidence_get_value(runner):
    with patch("envchain.cli_confidence.get_confidence", return_value="verified"):
        result = runner.invoke(
            confidence_group, ["get", "mychain", "--password", "secret"]
        )
        assert result.exit_code == 0
        assert "verified" in result.output


def test_confidence_get_unset(runner):
    with patch("envchain.cli_confidence.get_confidence", return_value=None):
        result = runner.invoke(
            confidence_group, ["get", "mychain", "--password", "secret"]
        )
        assert result.exit_code == 0
        assert "No confidence level" in result.output


def test_confidence_clear_success(runner):
    with patch("envchain.cli_confidence.clear_confidence") as mock_clear:
        result = runner.invoke(
            confidence_group, ["clear", "mychain", "--password", "secret"]
        )
        mock_clear.assert_called_once_with("mychain", "secret")
        assert result.exit_code == 0
        assert "cleared" in result.output


def test_confidence_list_all(runner):
    with patch(
        "envchain.cli_confidence.list_by_confidence",
        return_value={"chainA": "high", "chainB": "low"},
    ):
        result = runner.invoke(
            confidence_group, ["list", "--password", "secret"]
        )
        assert result.exit_code == 0
        assert "chainA" in result.output
        assert "high" in result.output


def test_confidence_list_empty(runner):
    with patch("envchain.cli_confidence.list_by_confidence", return_value={}):
        result = runner.invoke(
            confidence_group, ["list", "--password", "secret"]
        )
        assert result.exit_code == 0
        assert "No chains" in result.output
