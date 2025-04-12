
"""
mkplaylist - A tool to create Spotify playlists based on custom criteria using Last.fm data
"""

__version__ = '0.1.0'

# Import key modules for easier access
from mkplaylist.config import MkPlaylistConfig, config, data_dir, config_dir, cache_dir, state_dir, db_path, validate, status, sources
from mkplaylist import cli
