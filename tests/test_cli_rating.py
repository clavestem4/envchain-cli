"""Tests for CLI rating commands."""

import pytest
from click.testing import CliRunner
from unittest.mock import patch
from envchain.cli_rating import rating_group
from envchain.rating import RatingError


@pytest.fixture
def runner():
    return CliRunner()


def test_rating_set_success(runner):
    with patch("envchain.cli_rating.set_rating") as mock_set:
        result = runner.invoke(rating_group, ["set", "mychain", "4", "--password", "pw"])
        mock_set.assert_called_once_with("mychain", 4, "pw")
        assert "Rating 4 set" in result.output


def test_rating_set_invalid(runner):
    with patch("envchain.cli_rating.set_rating", side_effect=RatingError("bad")):
        result = runner.invoke(rating_group, ["set", "mychain", "9", "--password", "pw"])
        assert result.exit_code == 1
        assert "Error" in result.output


def test_rating_get_value(runner):
    with patch("envchain.cli_rating.get_rating", return_value=3):
        result = runner.invoke(rating_group, ["get", "mychain", "--password", "pw"])
        assert "3/5" in result.output


def test_rating_get_unset(runner):
    with patch("envchain.cli_rating.get_rating", return_value=None):
        result = runner.invoke(rating_group, ["get", "mychain", "--password", "pw"])
        assert "No rating" in result.output


def test_rating_clear_success(runner):
    with patch("envchain.cli_rating.clear_rating") as mock_clear:
        result = runner.invoke(rating_group, ["clear", "mychain", "--password", "pw"])
        mock_clear.assert_called_once_with("mychain", "pw")
        assert "cleared" in result.output


def test_rating_list_output(runner):
    with patch("envchain.cli_rating.list_by_rating", return_value=[("proj", 5), ("dev", 3)]):
        result = runner.invoke(rating_group, ["list", "--password", "pw"])
        assert "proj" in result.output
        assert "5/5" in result.output
        assert "dev" in result.output


def test_rating_list_empty(runner):
    with patch("envchain.cli_rating.list_by_rating", return_value=[]):
        result = runner.invoke(rating_group, ["list", "--password", "pw"])
        assert "No rated chains" in result.output
