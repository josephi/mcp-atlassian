"""URL-related utility functions for MCP Atlassian."""

import os
import re
from urllib.parse import urlparse


def is_atlassian_cloud_url(url: str) -> bool:
    """Determine if a URL belongs to Atlassian Cloud or Server/Data Center.

    Args:
        url: The URL to check

    Returns:
        True if the URL is for an Atlassian Cloud instance, False for Server/Data Center
    """
    # Localhost and IP-based URLs are always Server/Data Center
    if url is None or not url:
        return False

    parsed_url = urlparse(url)
    hostname = parsed_url.hostname or ""

    # Check for localhost or IP address
    if (
        hostname == "localhost"
        or re.match(r"^127\.", hostname)
        or re.match(r"^192\.168\.", hostname)
        or re.match(r"^10\.", hostname)
        or re.match(r"^172\.(1[6-9]|2[0-9]|3[0-1])\.", hostname)
    ):
        return False

    # The standard check for Atlassian cloud domains
    return (
        ".atlassian.net" in hostname
        or ".jira.com" in hostname
        or ".jira-dev.com" in hostname
    )


def is_cloud_instance(service: str, url: str | None = None) -> bool:
    """Determine if a service is running in cloud mode.
    
    This function checks both the explicit environment variable and the URL pattern
    to determine if a service is running in cloud mode.
    
    Args:
        service: The service to check ('jira' or 'confluence')
        url: Optional URL to check. If provided, this takes precedence over environment variables.
        
    Returns:
        True if the service is running in cloud mode, False for server/data center
        
    Raises:
        ValueError: If service is not 'jira' or 'confluence'
    """
    if service not in ["jira", "confluence"]:
        raise ValueError("Service must be either 'jira' or 'confluence'")
        
    service_upper = service.upper()
    is_cloud_env = f"{service_upper}_IS_CLOUD"
    is_cloud_setting = os.getenv(is_cloud_env)
    
    if is_cloud_setting is not None:
        return is_cloud_setting.lower() in ["true", "1", "yes"]
    
    if url is None:
        url = os.getenv(f"{service_upper}_URL")
        
    if not url:
        return False
        
    return is_atlassian_cloud_url(url)
