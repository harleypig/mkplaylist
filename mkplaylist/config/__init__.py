"""
Configuration package for mkplaylist.

This package provides a modular configuration system for mkplaylist,
with service-specific configurations for Spotify and Last.fm.
"""

import logging
import os
from pathlib import Path
from typing import Any, Dict, Optional

from mkplaylist.config.base import BaseConfig
from mkplaylist.config.spotify import SpotifyConfig
from mkplaylist.config.lastfm import LastfmConfig

# Set up logging
logger = logging.getLogger(__name__)


class MkPlaylistConfig(BaseConfig):
    """
    Main configuration class for mkplaylist.

    This class loads and manages service-specific configurations,
    and provides methods for accessing common configuration values.
    """

    def __init__(self):
        """
        Initialize the main configuration.

        Loads environment variables and initializes service-specific configurations.
        """
        super().__init__()

        # Load service-specific configurations
        self.spotify = SpotifyConfig()
        self.lastfm = LastfmConfig()

        # Load application settings
        # XXX: Add to documentation
        self.DEFAULT_SYNC_DAYS = self.get_env_int('MKPLAYLIST_DEFAULT_SYNC_DAYS', 30)
        self.LOG_LEVEL = self.get_env('LOG_LEVEL', 'INFO').upper()

    def validate(self) -> Dict[str, str]:
        """
        Validate the configuration and return any issues.

        Combines validation results from service-specific configurations
        and adds validation for application settings.

        Returns:
            Dict[str, str]: A dictionary of configuration issues, with keys as issue identifiers
                        and values as error messages. Empty if all is valid.
        """
        # Start with base validation
        issues = super().validate()

        # Add service-specific validation
        issues.update(self.spotify.validate())
        issues.update(self.lastfm.validate())

        # Add application settings validation
        if self.DEFAULT_SYNC_DAYS <= 0:
            issues['default_sync_days'] = 'Default sync days must be positive'

        if self.LOG_LEVEL not in ('DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'):
            issues['log_level'] = f'Invalid log level: {self.LOG_LEVEL}'

        return issues

    def status(self) -> Dict[str, bool]:
        """
        Get the status of various configuration items.

        Combines status results from service-specific configurations
        and adds status for application settings.

        Returns:
            Dict[str, bool]: A dictionary with configuration items as keys and their status as boolean values.
                         True indicates the item is properly configured.
        """
        # Start with base status
        status_dict = super().status()

        # Add service-specific status
        spotify_status = self.spotify.status()
        lastfm_status = self.lastfm.status()

        # Add prefixes to service-specific status keys
        for key, value in spotify_status.items():
            status_dict[f'spotify_{key}'] = value

        for key, value in lastfm_status.items():
            status_dict[f'lastfm_{key}'] = value

        # Add application settings status
        status_dict.update({
            'spotify_configured': all(spotify_status.values()),
            'lastfm_configured': all(lastfm_status.values()),
            'database_path_set': 'MKPLAYLIST_DB_PATH' in os.environ,
            'default_sync_days_valid': self.DEFAULT_SYNC_DAYS > 0,
            'log_level_valid': self.LOG_LEVEL in ('DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'),
        })

        return status_dict

    def sources(self) -> Dict[str, str]:
        """
        Get information about where each configuration value is coming from.

        Combines sources results from service-specific configurations
        and adds sources for application settings.

        Returns:
            Dict[str, str]: A dictionary with configuration items as keys and their sources as string values.
                        Possible sources: "Environment variable", ".env file",
                        ".env file (overriding environment variable)", or "Default value".
        """
        # Start with service-specific sources
        sources_dict = {}
        sources_dict.update(self.spotify.sources())
        sources_dict.update(self.lastfm.sources())

        # Add application settings sources
        sources_dict.update({
            'MKPLAYLIST_DEFAULT_SYNC_DAYS': self.source('MKPLAYLIST_DEFAULT_SYNC_DAYS'),
            'LOG_LEVEL': self.source('LOG_LEVEL'),
            'MKPLAYLIST_DB_PATH': self.source('MKPLAYLIST_DB_PATH'),
        })

        return sources_dict


# Create a singleton instance
config = MkPlaylistConfig()

# Export common methods for easier access
data_dir = config.data_dir
config_dir = config.config_dir
cache_dir = config.cache_dir
state_dir = config.state_dir
db_path = config.db_path
validate = config.validate
status = config.status
sources = config.sources
