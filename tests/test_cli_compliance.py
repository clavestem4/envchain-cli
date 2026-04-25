"""Tests for envchain.cli_compliance."""

import pytest
from click.testing import CliRunner
from unittest.mock import patch
from envchain.cli_compliance import compliance_group


@pytest.fixture()
def runner():
    return CliRunner()


def test_compliance_set_success(runner):
    with patch("envchain.cli_compliance.set_compliance") as mock_set:
        result = runner.invoke(compliance_group, ["set", "mychain", "SOC2", "--note", "Reviewed"])
        assert result.exit_code == 0
        assert "SOC2" in result.output
        mock_set.assert_called_once()


def test_compliance_set_invalid_standard(runner):
    from envchain.compliance import ComplianceError
    with patch("envchain.cli_compliance.set_compliance", side_effect=ComplianceError("Unknown standard 'BAD'")):
        result = runner.invoke(compliance_group, ["set", "mychain", "BAD"])
        assert result.exit_code == 1
        assert "Unknown standard" in result.output


def test_compliance_remove_success(runner):
    with patch("envchain.cli_compliance.remove_compliance") as mock_rm:
        result = runner.invoke(compliance_group, ["remove", "mychain", "HIPAA"])
        assert result.exit_code == 0
        assert "removed" in result.output
        mock_rm.assert_called_once()


def test_compliance_remove_not_set(runner):
    from envchain.compliance import ComplianceError
    with patch("envchain.cli_compliance.remove_compliance", side_effect=ComplianceError("not set")):
        result = runner.invoke(compliance_group, ["remove", "mychain", "PCI"])
        assert result.exit_code == 1
        assert "not set" in result.output


def test_compliance_get_with_tags(runner):
    with patch("envchain.cli_compliance.get_compliance", return_value={"GDPR": {"note": "EU law"}}):
        result = runner.invoke(compliance_group, ["get", "mychain"])
        assert result.exit_code == 0
        assert "GDPR" in result.output
        assert "EU law" in result.output


def test_compliance_get_empty(runner):
    with patch("envchain.cli_compliance.get_compliance", return_value={}):
        result = runner.invoke(compliance_group, ["get", "mychain"])
        assert result.exit_code == 0
        assert "No compliance tags" in result.output


def test_compliance_list_success(runner):
    with patch("envchain.cli_compliance.list_by_compliance", return_value=["chain_a", "chain_b"]):
        result = runner.invoke(compliance_group, ["list", "SOC2"])
        assert result.exit_code == 0
        assert "chain_a" in result.output
        assert "chain_b" in result.output


def test_compliance_list_invalid_standard(runner):
    result = runner.invoke(compliance_group, ["list", "BOGUS"])
    assert result.exit_code == 1
    assert "Unknown standard" in result.output


def test_compliance_list_empty(runner):
    with patch("envchain.cli_compliance.list_by_compliance", return_value=[]):
        result = runner.invoke(compliance_group, ["list", "NIST"])
        assert result.exit_code == 0
        assert "No chains tagged" in result.output
