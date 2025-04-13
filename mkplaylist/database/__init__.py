"""
Database package for mkplaylist.

This package contains the database models and operations for storing
and retrieving data from Spotify and Last.fm.
"""

# Engineering Core Modules
from mkplaylist.database.models import Base
from mkplaylist.database.models import Track
from mkplaylist.database.models import Playlist
from mkplaylist.database.models import PlaylistTrack
from mkplaylist.database.models import ListeningHistory
from mkplaylist.database.db_manager import DatabaseManager

__all__ = [
    "Base",
    "Track",
    "Playlist",
    "PlaylistTrack",
    "ListeningHistory",
    "DatabaseManager",
]
