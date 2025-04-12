"""
Configuration module for mkplaylist.

This module handles loading configuration from environment variables,
managing API credentials, and providing application settings.
"""

import os
from pathlib import Path
from typing import Optional, Dict, Any

from dotenv import load_dotenv

# Load environment variables from .env file if it exists
load_dotenv()

# Base directory for application data
def get_data_dir() -> Path:
    """Get the data directory for the application."""
    if os.name == 'nt':  # Windows
        base_dir = Path(os.environ.get('APPDATA', '')) / 'mkplaylist'
    else:  # Unix/Linux/Mac
        base_dir = Path(os.environ.get('XDG_DATA_HOME', Path.home() / '.local' / 'share')) / 'mkplaylist'
    
    # Create directory if it doesn't exist
    base_dir.mkdir(parents=True, exist_ok=True)
    return base_dir

# Database path
def get_db_path() -> Path:
    """Get the path to the SQLite database file."""
    custom_path = os.environ.get('MKPLAYLIST_DB_PATH')
    if custom_path:
        return Path(custom_path)
    return get_data_dir() / 'mkplaylist.db'

# Spotify API credentials
SPOTIFY_CLIENT_ID = os.environ.get('SPOTIFY_CLIENT_ID', '')
SPOTIFY_CLIENT_SECRET = os.environ.get('SPOTIFY_CLIENT_SECRET', '')
SPOTIFY_REDIRECT_URI = os.environ.get('SPOTIFY_REDIRECT_URI', 'http://localhost:8888/callback')

# Last.fm API credentials
LASTFM_API_KEY = os.environ.get('LASTFM_API_KEY', '')
LASTFM_API_SECRET = os.environ.get('LASTFM_API_SECRET', '')
LASTFM_USERNAME = os.environ.get('LASTFM_USERNAME', '')

# Application settings
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
