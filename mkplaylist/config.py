"""
Configuration module for mkplaylist.

This module handles loading configuration from environment variables,
managing API credentials, and providing application settings.
"""

import logging
import os
from pathlib import Path
from typing import Any, Dict

from dotenv import load_dotenv

# Set up logging
logger = logging.getLogger(__name__)

# Configuration precedence:
# 1. Environment variables are loaded first as baseline configuration
# 2. Values from .env file override environment variables if present
#
# First, get environment variables
env_vars = {key: value for key, value in os.environ.items()}

# Then load .env file which will override environment variables
load_dotenv(override=True)


# Base directory for application data
def get_data_dir() -> Path:
  """Get the data directory for the application."""
  if os.name == 'nt':                                      # Windows
    base_dir = Path(os.environ.get('APPDATA', '')) / 'mkplaylist'
  else:                                                    # Unix/Linux/Mac
    base_dir = Path(
      os.environ.get('XDG_DATA_HOME',
                     Path.home() / '.local' / 'share')
    ) / 'mkplaylist'

  # Create directory if it doesn't exist
  base_dir.mkdir(parents=True, exist_ok=True)
  return base_dir


def get_config_dir() -> Path:
  """
  Get the configuration directory for the application.

  Following XDG Base Directory Specification:
  - On Unix/Linux/Mac: $XDG_CONFIG_HOME/mkplaylist (~/.config/mkplaylist by default)
  - On Windows: %APPDATA%\\mkplaylist\\config

  Returns:
      Path: The configuration directory path
  """
  if os.name == 'nt':                            # Windows
    base_dir = Path(os.environ.get('APPDATA', '')) / 'mkplaylist' / 'config'
  else:                                          # Unix/Linux/Mac
    base_dir = Path(
      os.environ.get('XDG_CONFIG_HOME',
                     Path.home() / '.config')
    ) / 'mkplaylist'

  # Create directory if it doesn't exist
  base_dir.mkdir(parents=True, exist_ok=True)
  return base_dir


def get_cache_dir() -> Path:
  """
  Get the cache directory for the application.

  Following XDG Base Directory Specification:
  - On Unix/Linux/Mac: $XDG_CACHE_HOME/mkplaylist (~/.cache/mkplaylist by default)
  - On Windows: %LOCALAPPDATA%\\mkplaylist\\cache

  Returns:
      Path: The cache directory path
  """
  if os.name == 'nt':                            # Windows
    base_dir = Path(
      os.environ.get('LOCALAPPDATA', '')
    ) / 'mkplaylist' / 'cache'
  else:                                          # Unix/Linux/Mac
    base_dir = Path(
      os.environ.get('XDG_CACHE_HOME',
                     Path.home() / '.cache')
    ) / 'mkplaylist'

  # Create directory if it doesn't exist
  base_dir.mkdir(parents=True, exist_ok=True)
  return base_dir


def get_state_dir() -> Path:
  """
  Get the state directory for the application.

  Following XDG Base Directory Specification:
  - On Unix/Linux/Mac: $XDG_STATE_HOME/mkplaylist (~/.local/state/mkplaylist by default)
  - On Windows: %LOCALAPPDATA%\\mkplaylist\\state

  This directory is used for persistent application state data like authentication tokens.

  Returns:
      Path: The state directory path
  """
  if os.name == 'nt':                                      # Windows
    base_dir = Path(
      os.environ.get('LOCALAPPDATA', '')
    ) / 'mkplaylist' / 'state'
  else:                                                    # Unix/Linux/Mac
    base_dir = Path(
      os.environ.get('XDG_STATE_HOME',
                     Path.home() / '.local' / 'state')
    ) / 'mkplaylist'

  # Create directory if it doesn't exist
  base_dir.mkdir(parents=True, exist_ok=True)
  return base_dir


# Database path
def get_db_path() -> Path:
  """Get the path to the SQLite database file."""
  # Check for custom path in environment variable
  custom_path = os.environ.get('MKPLAYLIST_DB_PATH')
  if custom_path:
    return Path(custom_path)

  # Default path in data directory
  default_path = get_data_dir() / 'mkplaylist.db'

  # Check for database in old location (current directory)
  old_path = Path('mkplaylist.db')
  if old_path.exists() and not default_path.exists():
    try:
      # Create data directory if it doesn't exist (should be created by get_data_dir)
      data_dir = get_data_dir()
      data_dir.mkdir(parents=True, exist_ok=True)

      # Copy the database file to the new location
      import shutil
      shutil.copy2(old_path, default_path)
      logger.info(f"Migrated database from {old_path} to {default_path}")

      # Optionally remove the old database file
      # Uncomment the following line to remove the old database file after migration
      # old_path.unlink()
    except Exception as e:
      logger.warning(f"Failed to migrate database: {e}")

  return default_path


# Spotify API credentials
# These values will come from environment variables first, then be overridden by .env if present
SPOTIFY_CLIENT_ID = os.environ.get('SPOTIFY_CLIENT_ID', '')
SPOTIFY_CLIENT_SECRET = os.environ.get('SPOTIFY_CLIENT_SECRET', '')
SPOTIFY_REDIRECT_URI = os.environ.get(
  'SPOTIFY_REDIRECT_URI', 'http://localhost:8888/callback'
)

# Last.fm API credentials
# These values will come from environment variables first, then be overridden by .env if present
LASTFM_API_KEY = os.environ.get('LASTFM_API_KEY', '')
LASTFM_API_SECRET = os.environ.get('LASTFM_API_SECRET', '')
LASTFM_USERNAME = os.environ.get('LASTFM_USERNAME', '')

# Application settings
# These values will come from environment variables first, then be overridden by .env if present
DEFAULT_SYNC_DAYS = int(os.environ.get('MKPLAYLIST_DEFAULT_SYNC_DAYS', '30'))
LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO').upper()


def validate_config() -> Dict[str, Any]:
  """
    Validate the configuration and return any issues.

    Returns:
        A dictionary of configuration issues. Empty if all is valid.
    """
  issues = {}

  # Check Spotify credentials
  if not SPOTIFY_CLIENT_ID:
    issues['spotify_client_id'] = 'Missing Spotify Client ID'
  if not SPOTIFY_CLIENT_SECRET:
    issues['spotify_client_secret'] = 'Missing Spotify Client Secret'

  # Check Last.fm credentials
  if not LASTFM_API_KEY:
    issues['lastfm_api_key'] = 'Missing Last.fm API Key'
  if not LASTFM_API_SECRET:
    issues['lastfm_api_secret'] = 'Missing Last.fm API Secret'

  return issues


def get_config_status() -> Dict[str, bool]:
  """
    Get the status of various configuration items.

    Returns:
        A dictionary with configuration items and their status.
    """
  return {
    'spotify_configured': bool(SPOTIFY_CLIENT_ID and SPOTIFY_CLIENT_SECRET),
    'lastfm_configured': bool(LASTFM_API_KEY and LASTFM_API_SECRET),
    'database_path_set': 'MKPLAYLIST_DB_PATH' in os.environ,
    'lastfm_username_set': bool(LASTFM_USERNAME),
  }


def get_config_sources() -> Dict[str, str]:
  """
  Get information about where each configuration value is coming from.

  This helps users understand the configuration precedence:
  1. Environment variables are loaded first as baseline configuration
  2. Values from .env file override environment variables if present

  Returns:
      A dictionary with configuration items and their sources.
  """
  # Check if .env file exists
  dotenv_path = Path('.env')
  dotenv_exists = dotenv_path.exists()

  # Get original environment variables (before .env was loaded)
  original_env = env_vars

  # Check source for each configuration value
  sources = {}

  # Helper function to determine source
  def get_source(key: str, env_var_name: str) -> str:
    if not dotenv_exists:
      return "Environment variable" if env_var_name in original_env else "Default value"

    # If .env exists, check if value changed after loading .env
    if env_var_name in original_env:
      current_value = os.environ.get(env_var_name)
      original_value = original_env.get(env_var_name)

      if current_value != original_value:
        return ".env file (overriding environment variable)"
      return "Environment variable"

    if env_var_name in os.environ:
      return ".env file"

    return "Default value"

  # Check sources for all configuration values
  sources['SPOTIFY_CLIENT_ID'] = get_source(
    'SPOTIFY_CLIENT_ID', 'SPOTIFY_CLIENT_ID'
  )
  sources['SPOTIFY_CLIENT_SECRET'] = get_source(
    'SPOTIFY_CLIENT_SECRET', 'SPOTIFY_CLIENT_SECRET'
  )
  sources['SPOTIFY_REDIRECT_URI'] = get_source(
    'SPOTIFY_REDIRECT_URI', 'SPOTIFY_REDIRECT_URI'
  )
  sources['LASTFM_API_KEY'] = get_source('LASTFM_API_KEY', 'LASTFM_API_KEY')
  sources['LASTFM_API_SECRET'] = get_source(
    'LASTFM_API_SECRET', 'LASTFM_API_SECRET'
  )
  sources['LASTFM_USERNAME'] = get_source('LASTFM_USERNAME', 'LASTFM_USERNAME')
  sources['MKPLAYLIST_DB_PATH'] = get_source(
    'MKPLAYLIST_DB_PATH', 'MKPLAYLIST_DB_PATH'
  )
  sources['MKPLAYLIST_DEFAULT_SYNC_DAYS'] = get_source(
    'DEFAULT_SYNC_DAYS', 'MKPLAYLIST_DEFAULT_SYNC_DAYS'
  )
  sources['LOG_LEVEL'] = get_source('LOG_LEVEL', 'LOG_LEVEL')

  return sources
