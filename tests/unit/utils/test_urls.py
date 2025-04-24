"""Tests for the URL utilities module."""

import pytest
from unittest.mock import patch

from mcp_atlassian.utils.urls import is_atlassian_cloud_url, is_cloud_instance


def test_is_atlassian_cloud_url_empty():
    """Test that is_atlassian_cloud_url returns False for empty URL."""
    assert is_atlassian_cloud_url("") is False
    assert is_atlassian_cloud_url(None) is False


def test_is_atlassian_cloud_url_cloud():
    """Test that is_atlassian_cloud_url returns True for Atlassian Cloud URLs."""
    # Test standard Atlassian Cloud URLs
    assert is_atlassian_cloud_url("https://example.atlassian.net") is True
    assert is_atlassian_cloud_url("https://company.atlassian.net/wiki") is True
    assert is_atlassian_cloud_url("https://subdomain.atlassian.net/jira") is True
    assert is_atlassian_cloud_url("http://other.atlassian.net") is True

    # Test Jira Cloud specific domains
    assert is_atlassian_cloud_url("https://company.jira.com") is True
    assert is_atlassian_cloud_url("https://team.jira-dev.com") is True


def test_is_atlassian_cloud_url_server():
    """Test that is_atlassian_cloud_url returns False for Atlassian Server/Data Center URLs."""
    # Test with various server/data center domains
    assert is_atlassian_cloud_url("https://jira.example.com") is False
    assert is_atlassian_cloud_url("https://confluence.company.org") is False
    assert is_atlassian_cloud_url("https://jira.internal") is False


def test_is_atlassian_cloud_url_localhost():
    """Test that is_atlassian_cloud_url returns False for localhost URLs."""
    # Test with localhost
    assert is_atlassian_cloud_url("http://localhost") is False
    assert is_atlassian_cloud_url("http://localhost:8080") is False
    assert is_atlassian_cloud_url("https://localhost/jira") is False


def test_is_atlassian_cloud_url_ip_addresses():
    """Test that is_atlassian_cloud_url returns False for IP-based URLs."""
    # Test with IP addresses
    assert is_atlassian_cloud_url("http://127.0.0.1") is False
    assert is_atlassian_cloud_url("http://127.0.0.1:8080") is False
    assert is_atlassian_cloud_url("https://192.168.1.100") is False
    assert is_atlassian_cloud_url("https://10.0.0.1") is False
    assert is_atlassian_cloud_url("https://172.16.0.1") is False
    assert is_atlassian_cloud_url("https://172.31.255.254") is False


def test_is_atlassian_cloud_url_with_protocols():
    """Test that is_atlassian_cloud_url works with different protocols."""
    # Test with different protocols
    assert is_atlassian_cloud_url("https://example.atlassian.net") is True
    assert is_atlassian_cloud_url("http://example.atlassian.net") is True
    assert is_atlassian_cloud_url("ftp://example.atlassian.net") is True  # URL parsing still works


def test_is_cloud_instance_invalid_service():
    """Test that is_cloud_instance raises ValueError for invalid service."""
    with pytest.raises(ValueError, match="Service must be either 'jira' or 'confluence'"):
        is_cloud_instance("invalid")


def test_is_cloud_instance_explicit_setting():
    """Test that is_cloud_instance respects explicit environment variable settings."""
    test_cases = [
        # (service, is_cloud_value, expected_result)
        ("jira", "true", True),
        ("jira", "True", True),
        ("jira", "1", True),
        ("jira", "yes", True),
        ("jira", "false", False),
        ("jira", "False", False),
        ("jira", "0", False),
        ("jira", "no", False),
        ("confluence", "true", True),
        ("confluence", "false", False),
    ]
    
    for service, is_cloud_value, expected in test_cases:
        with patch.dict("os.environ", {
            f"{service.upper()}_IS_CLOUD": is_cloud_value,
        }, clear=True):
            assert is_cloud_instance(service) is expected


def test_is_cloud_instance_url_based():
    """Test that is_cloud_instance falls back to URL-based detection."""
    test_cases = [
        # (service, url, expected_result)
        ("jira", "https://example.atlassian.net", True),
        ("jira", "https://jira.example.com", False),
        ("confluence", "https://example.atlassian.net/wiki", True),
        ("confluence", "https://confluence.example.com", False),
    ]
    
    for service, url, expected in test_cases:
        with patch.dict("os.environ", {
            f"{service.upper()}_URL": url,
        }, clear=True):
            assert is_cloud_instance(service) is expected


def test_is_cloud_instance_no_url():
    """Test that is_cloud_instance defaults to server when no URL is present."""
    with patch.dict("os.environ", {}, clear=True):
        assert is_cloud_instance("jira") is False
        assert is_cloud_instance("confluence") is False


def test_is_cloud_instance_precedence():
    """Test that explicit setting takes precedence over URL-based detection."""
    test_cases = [
        # (is_cloud_value, url, expected_result)
        ("true", "https://jira.example.com", True),  # Explicit cloud overrides server URL
        ("false", "https://example.atlassian.net", False),  # Explicit server overrides cloud URL
    ]
    
    for is_cloud_value, url, expected in test_cases:
        with patch.dict("os.environ", {
            "JIRA_IS_CLOUD": is_cloud_value,
            "JIRA_URL": url,
        }, clear=True):
            assert is_cloud_instance("jira") is expected
