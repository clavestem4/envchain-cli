import pytest
from click.testing import CliRunner
from unittest.mock import patch, MagicMock
from datetime import datetime, timezone, timedelta
from envchain.cli_freshness import freshness_group


@pytest.fixture
def runner():
    return CliRunner()


def test_freshness_set_success(runner):
    with patch("envchain.cli_freshness.set_freshness") as mock_set:
        result = runner.invoke(freshness_group, ["set", "mychain", "7 days"])
        assert result.exit_code == 0
        assert "Freshness policy set" in result.output
        mock_set.assert_called_once()


def test_freshness_set_missing_chain(runner):
    from envchain.freshness import FreshnessError
    with patch("envchain.cli_freshness.set_freshness", side_effect=FreshnessError("not found")):
        result = runner.invoke(freshness_group, ["set", "ghost", "1 days"])
        assert result.exit_code == 1
        assert "Error" in result.output


def test_freshness_get_with_policy(runner):
    meta = {
        "max_age": "7 days",
        "updated_at": datetime.now(timezone.utc).isoformat()
    }
    with patch("envchain.cli_freshness.get_freshness", return_value=meta), \
         patch("envchain.cli_freshness.is_stale", return_value=False):
        result = runner.invoke(freshness_group, ["get", "mychain"])
        assert result.exit_code == 0
        assert "7 days" in result.output
        assert "stale: False" in result.output


def test_freshness_get_no_policy(runner):
    with patch("envchain.cli_freshness.get_freshness", return_value=None):
        result = runner.invoke(freshness_group, ["get", "mychain"])
        assert result.exit_code == 0
        assert "No freshness policy" in result.output


def test_freshness_clear_success(runner):
    with patch("envchain.cli_freshness.clear_freshness") as mock_clear:
        result = runner.invoke(freshness_group, ["clear", "mychain"])
        assert result.exit_code == 0
        assert "cleared" in result.output
        mock_clear.assert_called_once()


def test_freshness_stale_lists_chains(runner):
    with patch("envchain.cli_freshness.list_stale", return_value=["old_chain", "another"]):
        result = runner.invoke(freshness_group, ["stale"])
        assert result.exit_code == 0
        assert "old_chain" in result.output
        assert "another" in result.output


def test_freshness_stale_empty(runner):
    with patch("envchain.cli_freshness.list_stale", return_value=[]):
        result = runner.invoke(freshness_group, ["stale"])
        assert result.exit_code == 0
        assert "No stale chains" in result.output
