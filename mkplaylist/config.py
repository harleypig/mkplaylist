"""
Configuration module for mkplaylist.

This module handles loading configuration from environment variables,
managing API credentials, and providing application settings.
"""

import logging
import os
from pathlib import Path
from typing import Any, Dict, Optional

from dotenv import load_dotenv

# Set up logging
logger = logging.getLogger(__name__)

class MkPlaylistConfig:
    """
    Configuration class for mkplaylist.
    
    This class handles loading configuration from environment variables,
    managing API credentials, and providing application settings.
    """
    
    def __init__(self):
        """Initialize the configuration."""
        # Store original environment variables before loading .env
        self.env_vars = {key: value for key, value in os.environ.items()}
        
        # Load .env file which will override environment variables
        load_dotenv(override=True)
        
        # Load Spotify API credentials
        self.SPOTIFY_CLIENT_ID = os.environ.get('SPOTIFY_CLIENT_ID', '')
        self.SPOTIFY_CLIENT_SECRET = os.environ.get('SPOTIFY_CLIENT_SECRET', '')
        self.SPOTIFY_REDIRECT_URI = os.environ.get(
            'SPOTIFY_REDIRECT_URI', 'http://localhost:8888/callback'
        )
        
        # Load Last.fm API credentials
        self.LASTFM_API_KEY = os.environ.get('LASTFM_API_KEY', '')
        self.LASTFM_API_SECRET = os.environ.get('LASTFM_API_SECRET', '')
        self.LASTFM_USERNAME = os.environ.get('LASTFM_USERNAME', '')
        
        # Load application settings
        self.DEFAULT_SYNC_DAYS = int(os.environ.get('MKPLAYLIST_DEFAULT_SYNC_DAYS', '30'))
        self.LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO').upper()
    
    def get_data_dir(self) -> Path:
        """
        Get the data directory for the application.
        
        Returns:
            Path: The data directory path
        """
        if os.name == 'nt':  # Windows
            data_dir = Path(os.environ.get('APPDATA', '')) / 'mkplaylist'
        else:  # Unix/Linux/Mac
            data_dir = Path(
                os.environ.get('XDG_DATA_HOME',
                               Path.home() / '.local' / 'share')
            ) / 'mkplaylist'
        
        # Create directory if it doesn't exist
        data_dir.mkdir(parents=True, exist_ok=True)
        return data_dir
    
    def get_config_dir(self) -> Path:
        """
        Get the configuration directory for the application.
        
        Following XDG Base Directory Specification:
        - On Unix/Linux/Mac: $XDG_CONFIG_HOME/mkplaylist (~/.config/mkplaylist by default)
        - On Windows: %APPDATA%\mkplaylist\config
        
        Returns:
            Path: The configuration directory path
        """
        if os.name == 'nt':  # Windows
            config_dir = Path(os.environ.get('APPDATA', '')) / 'mkplaylist' / 'config'
        else:  # Unix/Linux/Mac
            config_dir = Path(
                os.environ.get('XDG_CONFIG_HOME',
                               Path.home() / '.config')
            ) / 'mkplaylist'
        
        # Create directory if it doesn't exist
        config_dir.mkdir(parents=True, exist_ok=True)
        return config_dir
    
    def get_cache_dir(self) -> Path:
        """
        Get the cache directory for the application.
        
        Following XDG Base Directory Specification:
        - On Unix/Linux/Mac: $XDG_CACHE_HOME/mkplaylist (~/.cache/mkplaylist by default)
        - On Windows: %LOCALAPPDATA%\mkplaylist\cache
        
        Returns:
            Path: The cache directory path
        """
        if os.name == 'nt':  # Windows
            cache_dir = Path(os.environ.get('LOCALAPPDATA', '')) / 'mkplaylist' / 'cache'
        else:  # Unix/Linux/Mac
            cache_dir = Path(
                os.environ.get('XDG_CACHE_HOME',
                               Path.home() / '.cache')
            ) / 'mkplaylist'
        
        # Create directory if it doesn't exist
        cache_dir.mkdir(parents=True, exist_ok=True)
        return cache_dir
    
    def get_state_dir(self) -> Path:
        """
        Get the state directory for the application.
        
        Following XDG Base Directory Specification:
        - On Unix/Linux/Mac: $XDG_STATE_HOME/mkplaylist (~/.local/state/mkplaylist by default)
        - On Windows: %LOCALAPPDATA%\mkplaylist\state
        
        This directory is used for persistent application state data like authentication tokens.
        
        Returns:
            Path: The state directory path
        """
        if os.name == 'nt':  # Windows
            state_dir = Path(os.environ.get('LOCALAPPDATA', '')) / 'mkplaylist' / 'state'
        else:  # Unix/Linux/Mac
            state_dir = Path(
                os.environ.get('XDG_STATE_HOME',
                               Path.home() / '.local' / 'state')
            ) / 'mkplaylist'
        
        # Create directory if it doesn't exist
        state_dir.mkdir(parents=True, exist_ok=True)
        return state_dir
    
    def get_db_path(self) -> Path:
        """
        Get the path to the SQLite database file.
        
        Returns:
            Path: The database file path
        """
        # Check for custom path in environment variable
        custom_path = os.environ.get('MKPLAYLIST_DB_PATH')
        if custom_path:
            return Path(custom_path)
        
        # Default path in data directory
        default_path = self.get_data_dir() / 'mkplaylist.db'
        return default_path
    
    def validate_config(self) -> Dict[str, Any]:
        """
        Validate the configuration and return any issues.
        
        Returns:
            A dictionary of configuration issues. Empty if all is valid.
        """
        issues = {}
        
        # Check Spotify credentials
        if not self.SPOTIFY_CLIENT_ID:
            issues['spotify_client_id'] = 'Missing Spotify Client ID'
        if not self.SPOTIFY_CLIENT_SECRET:
            issues['spotify_client_secret'] = 'Missing Spotify Client Secret'
        
        # Check Last.fm credentials
        if not self.LASTFM_API_KEY:
            issues['lastfm_api_key'] = 'Missing Last.fm API Key'
        if not self.LASTFM_API_SECRET:
            issues['lastfm_api_secret'] = 'Missing Last.fm API Secret'
        
        return issues
    
    def get_config_status(self) -> Dict[str, bool]:
        """
        Get the status of various configuration items.
        
        Returns:
            A dictionary with configuration items and their status.
        """
        return {
            'spotify_configured': bool(self.SPOTIFY_CLIENT_ID and self.SPOTIFY_CLIENT_SECRET),
            'lastfm_configured': bool(self.LASTFM_API_KEY and self.LASTFM_API_SECRET),
            'database_path_set': 'MKPLAYLIST_DB_PATH' in os.environ,
            'lastfm_username_set': bool(self.LASTFM_USERNAME),
        }
    
    def get_config_sources(self) -> Dict[str, str]:
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
        original_env = self.env_vars
        
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


# Create a singleton instance for backward compatibility
config = MkPlaylistConfig()

# Module-level functions for backward compatibility
def get_data_dir() -> Path:
    """Get the data directory for the application."""
    return config.get_data_dir()

def get_config_dir() -> Path:
    """Get the configuration directory for the application."""
    return config.get_config_dir()

def get_cache_dir() -> Path:
    """Get the cache directory for the application."""
    return config.get_cache_dir()

def get_state_dir() -> Path:
    """Get the state directory for the application."""
    return config.get_state_dir()

def get_db_path() -> Path:
    """Get the path to the SQLite database file."""
    return config.get_db_path()

def validate_config() -> Dict[str, Any]:
    """Validate the configuration and return any issues."""
    return config.validate_config()

def get_config_status() -> Dict[str, bool]:
    """Get the status of various configuration items."""
    return config.get_config_status()

def get_config_sources() -> Dict[str, str]:
    """Get information about where each configuration value is coming from."""
    return config.get_config_sources()

# Expose configuration variables at module level for backward compatibility
SPOTIFY_CLIENT_ID = config.SPOTIFY_CLIENT_ID
SPOTIFY_CLIENT_SECRET = config.SPOTIFY_CLIENT_SECRET
SPOTIFY_REDIRECT_URI = config.SPOTIFY_REDIRECT_URI
LASTFM_API_KEY = config.LASTFM_API_KEY
LASTFM_API_SECRET = config.LASTFM_API_SECRET
LASTFM_USERNAME = config.LASTFM_USERNAME
DEFAULT_SYNC_DAYS = config.DEFAULT_SYNC_DAYS
LOG_LEVEL = config.LOG_LEVEL
