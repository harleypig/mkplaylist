
"""
Spotify configuration module for mkplaylist.

This module provides Spotify-specific configuration, including API credentials
and validation.
"""

import logging
import re
from typing import Dict, Any, List, Tuple

from mkplaylist.config.base import BaseConfig, ValidationRules, required, exact_length, pattern, is_url

# Set up logging
logger = logging.getLogger(__name__)

# Spotify-specific validation rules
def is_valid_client_id(value: str) -> Tuple[bool, str]:
    """Validate that a value is a valid Spotify Client ID."""
    if not value:
        return False, "Spotify Client ID cannot be empty"
    if len(value) != 32:
        return False, "Spotify Client ID must be 32 characters long"
    if not value.isalnum():
        return False, "Spotify Client ID must contain only alphanumeric characters"
    return True, ""

def is_valid_client_secret(value: str) -> Tuple[bool, str]:
    """Validate that a value is a valid Spotify Client Secret."""
    if not value:
        return False, "Spotify Client Secret cannot be empty"
    if len(value) != 32:
        return False, "Spotify Client Secret must be 32 characters long"
    if not value.isalnum():
        return False, "Spotify Client Secret must contain only alphanumeric characters"
    return True, ""

def is_valid_redirect_uri(value: str) -> Tuple[bool, str]:
    """Validate that a value is a valid Spotify Redirect URI."""
    if not value:
        return False, "Spotify Redirect URI cannot be empty"
    if not value.startswith(('http://', 'https://')):
        return False, "Spotify Redirect URI must start with http:// or https://"
    return True, ""

class SpotifyConfig(BaseConfig):
    """
    Spotify configuration class for mkplaylist.

    This class handles loading Spotify-specific configuration from environment
    variables, managing API credentials, and providing validation.
    """

    def __init__(self):
        """
        Initialize the Spotify configuration.

        Loads environment variables and initializes configuration attributes
        for Spotify API credentials.
        """
        super().__init__()

        # Load Spotify API credentials
        self.CLIENT_ID = self.get_env('SPOTIFY_CLIENT_ID', '')
        self.CLIENT_SECRET = self.get_env('SPOTIFY_CLIENT_SECRET', '')
        self.REDIRECT_URI = self.get_env(
            'SPOTIFY_REDIRECT_URI', 'http://localhost:8888/callback'
        )

        # Define validation rules
        self.validation_rules: ValidationRules = {
            'CLIENT_ID': [required, is_valid_client_id],
            'CLIENT_SECRET': [required, is_valid_client_secret],
            'REDIRECT_URI': [required, is_valid_redirect_uri],
        }

    def validate(self) -> Dict[str, str]:
        """
        Validate the Spotify configuration and return any issues.

        Checks that required API credentials are set and properly formatted.

        Returns:
            Dict[str, str]: A dictionary of configuration issues, with keys as issue identifiers
                            and values as error messages. Empty if all is valid.
        """
        # Get values to validate
        values = {
            'CLIENT_ID': self.CLIENT_ID,
            'CLIENT_SECRET': self.CLIENT_SECRET,
            'REDIRECT_URI': self.REDIRECT_URI,
        }

        # Validate using rules
        issues = self._validate_with_rules(values, self.validation_rules)

        # Map internal keys to user-friendly keys
        user_friendly_issues = {}
        key_mapping = {
            'CLIENT_ID': 'spotify_client_id',
            'CLIENT_SECRET': 'spotify_client_secret',
            'REDIRECT_URI': 'spotify_redirect_uri',
        }

        for key, message in issues.items():
            user_friendly_key = key_mapping.get(key, key)
            user_friendly_issues[user_friendly_key] = message

        return user_friendly_issues

    def status(self) -> Dict[str, bool]:
        """
        Get the status of Spotify configuration items.

        Provides a quick overview of which Spotify configuration components
        are properly set up.

        Returns:
            Dict[str, bool]: A dictionary with configuration items as keys and their status as boolean values.
                             True indicates the item is properly configured.
        """
        # Validate each credential individually
        client_id_valid = all(rule(self.CLIENT_ID)[0] for rule in self.validation_rules['CLIENT_ID'])
        client_secret_valid = all(rule(self.CLIENT_SECRET)[0] for rule in self.validation_rules['CLIENT_SECRET'])
        redirect_uri_valid = all(rule(self.REDIRECT_URI)[0] for rule in self.validation_rules['REDIRECT_URI'])

        return {
            'client_id_configured': client_id_valid,
            'client_secret_configured': client_secret_valid,
            'redirect_uri_configured': redirect_uri_valid,
        }

    def sources(self) -> Dict[str, str]:
        """
        Get information about where each Spotify configuration value is coming from.

        Helps users understand the configuration precedence by identifying whether each value
        comes from environment variables, .env file, or default values.

        Returns:
            Dict[str, str]: A dictionary with configuration items as keys and their sources as string values.
                            Possible sources: "Environment variable", ".env file",
                            ".env file (overriding environment variable)", or "Default value".
        """
        return {
            'SPOTIFY_CLIENT_ID': self.source('SPOTIFY_CLIENT_ID'),
            'SPOTIFY_CLIENT_SECRET': self.source('SPOTIFY_CLIENT_SECRET'),
            'SPOTIFY_REDIRECT_URI': self.source('SPOTIFY_REDIRECT_URI'),
        }
