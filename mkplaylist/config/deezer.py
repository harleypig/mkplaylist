"""
Deezer configuration module for mkplaylist.

This module provides Deezer-specific configuration, including API credentials
and validation.
import logging
import re
from typing import Dict, Any, List, Tuple

from mkplaylist.config.base import ServiceConfig, ValidationRules, required, exact_length, pattern, is_url
"""
# Set up logging
logger = logging.getLogger(__name__)

# Deezer-specific validation rules
def is_valid_app_id(value: str) -> Tuple[bool, str]:
    """Validate that a value is a valid Deezer Application ID."""
    if not value:
        return False, "Deezer Application ID cannot be empty"
    try:
        app_id = int(value)
        if app_id <= 0:
            return False, "Deezer Application ID must be a positive integer"
        return True, ""
    except ValueError:
        return False, "Deezer Application ID must be a valid integer"

def is_valid_app_secret(value: str) -> Tuple[bool, str]:
    """Validate that a value is a valid Deezer Application Secret."""
    if not value:
        return False, "Deezer Application Secret cannot be empty"
    if len(value) < 32:
        return False, "Deezer Application Secret must be at least 32 characters long"
    # Deezer secrets are typically alphanumeric
    if not re.match(r'^[a-zA-Z0-9]+$', value):
        return False, "Deezer Application Secret must contain only alphanumeric characters"
    return True, ""

def is_valid_access_token(value: str) -> Tuple[bool, str]:
    """Validate that a value is a valid Deezer Access Token."""
    # Access token can be empty as it might be obtained during authentication
    if not value:
        return True, ""
    if len(value) < 20:
        return False, "Deezer Access Token must be at least 20 characters long"
    # Deezer tokens are typically alphanumeric
    if not re.match(r'^[a-zA-Z0-9]+$', value):
        return False, "Deezer Access Token must contain only alphanumeric characters"
    return True, ""


class DeezerConfig(ServiceConfig):
    """
    Deezer configuration class for mkplaylist.

    This class handles loading Deezer-specific configuration from environment
    variables, managing API credentials, and providing validation.
    """
    
    @property
    def service_name(self) -> str:
        """
        Get the name of the service.
        
        Returns:
            str: The name of the service ('deezer')
        """
        return 'deezer'

    def __init__(self):
        """
        Initialize the Deezer configuration.

        Loads environment variables and initializes configuration attributes
        for Deezer API credentials.
        """
        super().__init__()

        # Load Deezer API credentials
        self.APP_ID = self.get_env('DEEZER_APP_ID', '')
        self.APP_SECRET = self.get_env('DEEZER_APP_SECRET', '')
        self.ACCESS_TOKEN = self.get_env('DEEZER_ACCESS_TOKEN', '')
        self.REDIRECT_URI = self.get_env(
            'DEEZER_REDIRECT_URI', 'http://localhost:8888/callback'
        )

        # Define validation rules
        self.validation_rules: ValidationRules = {
            'APP_ID': [required, is_valid_app_id],
            'APP_SECRET': [required, is_valid_app_secret],
            'ACCESS_TOKEN': [is_valid_access_token],  # Optional
            'REDIRECT_URI': [required, is_url],
        }

    def validate(self) -> Dict[str, str]:
        """
        Validate the Deezer configuration and return any issues.

        Checks that required API credentials are set and properly formatted.

        Returns:
            Dict[str, str]: A dictionary of configuration issues, with keys as issue identifiers
                        and values as error messages. Empty if all is valid.
        """
        # Get values to validate
        values = {
            'APP_ID': self.APP_ID,
            'APP_SECRET': self.APP_SECRET,
            'ACCESS_TOKEN': self.ACCESS_TOKEN,
            'REDIRECT_URI': self.REDIRECT_URI,
        }

        # Validate using rules
        issues = self._validate_with_rules(values, self.validation_rules)

        # Map internal keys to user-friendly keys
        user_friendly_issues = {}
        key_mapping = {
            'APP_ID': 'deezer_app_id',
            'APP_SECRET': 'deezer_app_secret',
            'ACCESS_TOKEN': 'deezer_access_token',
            'REDIRECT_URI': 'deezer_redirect_uri',
        }

        for key, message in issues.items():
            user_friendly_key = key_mapping.get(key, key)
            user_friendly_issues[user_friendly_key] = message

        return user_friendly_issues

    def status(self) -> Dict[str, bool]:
        """
        Get the status of Deezer configuration items.

        Provides a quick overview of which Deezer configuration components
        are properly set up.

        Returns:
            Dict[str, bool]: A dictionary with configuration items as keys and their status as boolean values.
                         True indicates the item is properly configured.
        """
        # Validate each credential individually
        app_id_valid = all(rule(self.APP_ID)[0] for rule in self.validation_rules['APP_ID'])
        app_secret_valid = all(rule(self.APP_SECRET)[0] for rule in self.validation_rules['APP_SECRET'])
        access_token_valid = all(rule(self.ACCESS_TOKEN)[0] for rule in self.validation_rules['ACCESS_TOKEN'])
        redirect_uri_valid = all(rule(self.REDIRECT_URI)[0] for rule in self.validation_rules['REDIRECT_URI'])

        return {
            'app_id_configured': app_id_valid,
            'app_secret_configured': app_secret_valid,
            'access_token_configured': access_token_valid,
            'redirect_uri_configured': redirect_uri_valid,
        }

    def sources(self) -> Dict[str, str]:
        """
        Get information about where each Deezer configuration value is coming from.

        Helps users understand the configuration precedence by identifying whether each value
        comes from environment variables, .env file, or default values.

        Returns:
            Dict[str, str]: A dictionary with configuration items as keys and their sources as string values.
                        Possible sources: "Environment variable", ".env file",
                        ".env file (overriding environment variable)", or "Default value".
        """
        return {
            'DEEZER_APP_ID': self.source('DEEZER_APP_ID'),
            'DEEZER_APP_SECRET': self.source('DEEZER_APP_SECRET'),
            'DEEZER_ACCESS_TOKEN': self.source('DEEZER_ACCESS_TOKEN'),
            'DEEZER_REDIRECT_URI': self.source('DEEZER_REDIRECT_URI'),
        }

