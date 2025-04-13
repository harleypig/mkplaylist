"""
Configuration package for mkplaylist.

This package provides a modular configuration system for mkplaylist,
with service-specific configurations that are automatically discovered and loaded.
"""

import importlib
import inspect
import logging
import os
import pkgutil
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Type

from mkplaylist.config.base import BaseConfig, ServiceConfig

# Set up logging
logger = logging.getLogger(__name__)

# Dictionary to store service configuration classes
_service_configs: Dict[str, Type[ServiceConfig]] = {}


def register_service_config(config_class: Type[ServiceConfig]) -> None:
  """
    Register a service configuration class.

    This function is used to register service configuration classes so they can be
    automatically loaded by the main configuration class.

    Args:
        config_class: The service configuration class to register.
    """
  # Create an instance to get the service name
  try:
    instance = config_class()
    service_name = instance.service_name
    _service_configs[service_name] = config_class
    logger.debug(f"Registered service configuration for '{service_name}'")
  except Exception as e:
    logger.warning(
      f"Failed to register service configuration {config_class.__name__}: {e}"
    )


def discover_service_configs() -> None:
  """
    Discover and register service configuration classes.

    This function scans the mkplaylist.config package for modules that define
    service configuration classes (subclasses of ServiceConfig) and registers them.
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
    'spotify_configured':
      all(spotify_status.values()),
    'lastfm_configured':
      all(lastfm_status.values()),
    'database_path_set':
      'MKPLAYLIST_DB_PATH' in os.environ,
    'default_sync_days_valid':
      self.DEFAULT_SYNC_DAYS > 0,
    'log_level_valid':
      self.LOG_LEVEL in ('DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'),
  })

  return status_dict


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

    # Dictionary to store service configurations
    self._services: Dict[str, ServiceConfig] = {}

    # Discover and load service configurations
    discover_service_configs()
    self._load_service_configs()

    # Load application settings
    # XXX: Add to documentation
    self.DEFAULT_SYNC_DAYS = self.get_env_int(
      'MKPLAYLIST_DEFAULT_SYNC_DAYS', 30
    )
    self.LOG_LEVEL = self.get_env('LOG_LEVEL', 'INFO').upper()

  def _load_service_configs(self) -> None:
    """
        Load service configurations.

        This method creates instances of all registered service configuration classes
        and stores them in the _services dictionary.
        """
    for service_name, config_class in _service_configs.items():
      try:
        self._services[service_name] = config_class()
        logger.debug(f"Loaded service configuration for '{service_name}'")

        # Add service as an attribute for backward compatibility
        # This allows accessing service configs like config.spotify and config.lastfm
        if not hasattr(self, service_name):
          setattr(self, service_name, self._services[service_name])
      except Exception as e:
        logger.warning(
          f"Failed to load service configuration for '{service_name}': {e}"
        )

  def get_service(self, service_name: str) -> Optional[ServiceConfig]:
    """
        Get a service configuration by name.

        Args:
            service_name: The name of the service.

        Returns:
            The service configuration, or None if not found.
        """
    return self._services.get(service_name)

  def get_services(self) -> Dict[str, ServiceConfig]:
    """
        Get all service configurations.

        Returns:
            A dictionary of service configurations, with service names as keys.
        """
    return self._services.copy()

  def get_service_names(self) -> List[str]:
    """
        Get the names of all loaded services.

        Returns:
            A list of service names.
        """
    return list(self._services.keys())

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
    for service_name, service_config in self._services.items():
      service_issues = service_config.validate()
      # Add service name prefix to issue keys
      for key, value in service_issues.items():
        issues[f"{service_name}_{key}"] = value

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
    for service_name, service_config in self._services.items():
      service_status = service_config.status()

      # Add prefixes to service-specific status keys
      for key, value in service_status.items():
        status_dict[f"{service_name}_{key}"] = value

      # Add overall service status
      status_dict[f"{service_name}_configured"] = all(service_status.values())

    # Add application settings status
    status_dict.update({
      'database_path_set':
        'MKPLAYLIST_DB_PATH' in os.environ,
      'default_sync_days_valid':
        self.DEFAULT_SYNC_DAYS > 0,
      'log_level_valid':
        self.LOG_LEVEL in ('DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'),
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
    for service_config in self._services.values():
      sources_dict.update(service_config.sources())

    # Add application settings sources
    sources_dict.update({
      'MKPLAYLIST_DEFAULT_SYNC_DAYS':
        self.source('MKPLAYLIST_DEFAULT_SYNC_DAYS'),
      'LOG_LEVEL':
        self.source('LOG_LEVEL'),
      'MKPLAYLIST_DB_PATH':
        self.source('MKPLAYLIST_DB_PATH'),
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
get_service = config.get_service
get_services = config.get_services
get_service_names = config.get_service_names

# Export ServiceConfig for creating new service configurations
from mkplaylist.config.base import ServiceConfig
