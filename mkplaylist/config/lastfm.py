
"""
Last.fm configuration module for mkplaylist.

This module provides Last.fm-specific configuration, including API credentials
and validation.
"""

import logging
import re
from typing import Dict, Any, List, Tuple
from mkplaylist.config.base import ServiceConfig, ValidationRules, required, exact_length, pattern


# Set up logging
logger = logging.getLogger(__name__)

# Last.fm-specific validation rules
def is_valid_api_key(value: str) -> Tuple[bool, str]:
    """Validate that a value is a valid Last.fm API Key."""
    if not value:
        return False, "Last.fm API Key cannot be empty"
    if len(value) != 32:
        return False, "Last.fm API Key must be 32 characters long"
    try:
        int(value, 16)
        return True, ""
    except ValueError:
        return False, "Last.fm API Key must be a valid hexadecimal string"

def is_valid_api_secret(value: str) -> Tuple[bool, str]:
    """Validate that a value is a valid Last.fm API Secret."""
    if not value:
        return False, "Last.fm API Secret cannot be empty"
    if len(value) != 32:
        return False, "Last.fm API Secret must be 32 characters long"
    try:
        int(value, 16)
        return True, ""
    except ValueError:
        return False, "Last.fm API Secret must be a valid hexadecimal string"

def is_valid_username(value: str) -> Tuple[bool, str]:
    """Validate that a value is a valid Last.fm username."""
    if not value:
        return False, "Last.fm username cannot be empty"
    if not re.match(r'^[a-zA-Z0-9_-]+$', value):
        return False, "Last.fm username must contain only alphanumeric characters, underscores, and hyphens"
    return True, ""

class LastfmConfig(ServiceConfig):
    """
    Last.fm configuration class for mkplaylist.
    
    This class handles loading Last.fm-specific configuration from environment
    variables, managing API credentials, and providing validation.
    """
    @property
    def service_name(self) -> str:
        """
        Get the name of the service.
        
        Returns:
            str: The name of the service ('lastfm')
        """
        return 'lastfm'
    
    def __init__(self):
        """
        Initialize the Last.fm configuration.

        Loads environment variables and initializes configuration attributes
        for Last.fm API credentials.
        """
        super().__init__()

        # Load Last.fm API credentials
        self.API_KEY = self.get_env('LASTFM_API_KEY', '')
        self.API_SECRET = self.get_env('LASTFM_API_SECRET', '')
        self.USERNAME = self.get_env('LASTFM_USERNAME', '')

        # Define validation rules
        self.validation_rules: ValidationRules = {
            'API_KEY': [required, is_valid_api_key],
            'API_SECRET': [required, is_valid_api_secret],
            'USERNAME': [required, is_valid_username],
        }

    def validate(self) -> Dict[str, str]:
        """
        Validate the Last.fm configuration and return any issues.

        Checks that required API credentials are set and properly formatted.

        Returns:
            Dict[str, str]: A dictionary of configuration issues, with keys as issue identifiers
                        and values as error messages. Empty if all is valid.
        """
        # Get values to validate
        values = {
            'API_KEY': self.API_KEY,
            'API_SECRET': self.API_SECRET,
            'USERNAME': self.USERNAME,
        }

        # Validate using rules
        issues = self._validate_with_rules(values, self.validation_rules)

        # Map internal keys to user-friendly keys
        user_friendly_issues = {}
        key_mapping = {
            'API_KEY': 'lastfm_api_key',
            'API_SECRET': 'lastfm_api_secret',
            'USERNAME': 'lastfm_username',
        }

        for key, message in issues.items():
            user_friendly_key = key_mapping.get(key, key)
            user_friendly_issues[user_friendly_key] = message

        return user_friendly_issues

    def status(self) -> Dict[str, bool]:
        """
        Get the status of Last.fm configuration items.

        Provides a quick overview of which Last.fm configuration components
        are properly set up.

        Returns:
            Dict[str, bool]: A dictionary with configuration items as keys and their status as boolean values.
                         True indicates the item is properly configured.
        """
        # Validate each credential individually
        api_key_valid = all(rule(self.API_KEY)[0] for rule in self.validation_rules['API_KEY'])
        api_secret_valid = all(rule(self.API_SECRET)[0] for rule in self.validation_rules['API_SECRET'])
        username_valid = all(rule(self.USERNAME)[0] for rule in self.validation_rules['USERNAME'])

        return {
            'api_key_configured': api_key_valid,
            'api_secret_configured': api_secret_valid,
            'username_configured': username_valid,
            'api_key_configured': bool(self.API_KEY and self._is_valid_api_key(self.API_KEY)),
            'api_secret_configured': bool(self.API_SECRET and self._is_valid_api_secret(self.API_SECRET)),
            'username_configured': bool(self.USERNAME),
        }

    def sources(self) -> Dict[str, str]:
        """
        Get information about where each Last.fm configuration value is coming from.

        Helps users understand the configuration precedence by identifying whether each value
        comes from environment variables, .env file, or default values.

        Returns:
            Dict[str, str]: A dictionary with configuration items as keys and their sources as string values.

    
                        ".env file (overriding environment variable)", or "Default value".
        """
        return {
            'LASTFM_API_KEY': self.source('LASTFM_API_KEY'),
            'LASTFM_API_SECRET': self.source('LASTFM_API_SECRET'),
            'LASTFM_USERNAME': self.source('LASTFM_USERNAME'),
        }


