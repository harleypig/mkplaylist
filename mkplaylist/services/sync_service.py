"""
Sync service for mkplaylist.

This module provides a service for synchronizing data from Spotify and Last.fm.
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union

from mkplaylist.api.spotify_client import SpotifyClient
from mkplaylist.api.lastfm_client import LastFmClient
from mkplaylist.database.db_manager import DatabaseManager

logger = logging.getLogger(__name__)


class SyncService:

  """Service for synchronizing data from Spotify and Last.fm."""

  def __init__(
    self,
    db_manager: Optional[DatabaseManager] = None,
    spotify_client: Optional[SpotifyClient] = None,
    lastfm_client: Optional[LastFmClient] = None
  ):
    """
        Initialize the sync service.

        Args:
            db_manager: Database manager instance
            spotify_client: Spotify client instance
            lastfm_client: Last.fm client instance
        """
    self.db_manager = db_manager or DatabaseManager()
    self.spotify_client = spotify_client or SpotifyClient()
    self.lastfm_client = lastfm_client or LastFmClient()

    # Ensure database tables exist
    self.db_manager.create_tables()

  def sync_spotify_playlists(self, full_sync: bool = False) -> Dict[str, Any]:
    """
        Sync playlists from Spotify.

        Args:
            full_sync: Whether to perform a full sync

        Returns:
            Summary of the sync operation
        """
    logger.info("Syncing Spotify playlists...")

    # Authenticate with Spotify
    self.spotify_client.authenticate()

    # Get user playlists
    playlists = self.spotify_client.get_user_playlists()
    logger.info(f"Found {len(playlists)} playlists")

    # Track sync statistics
    stats = {
      'playlists_synced': 0,
      'tracks_synced': 0,
      'new_playlists': 0,
      'new_tracks': 0,
      'updated_playlists': 0,
      'updated_tracks': 0,
    }

    # Sync each playlist
    for playlist in playlists:
      playlist_id = playlist['id']
      playlist_name = playlist['name']

      # Check if playlist exists in database
      db_playlist = self.db_manager.get_playlist_by_spotify_id(playlist_id)
      is_new_playlist = db_playlist is None

      # Add or update playlist in database
      playlist_data = {
        'spotify_id': playlist_id,
        'name': playlist_name,
        'description': playlist.get('description', ''),
        'owner': playlist['owner']['id'],
        'is_public': playlist.get('public', False),
      }
      db_playlist = self.db_manager.add_playlist(playlist_data)

      if is_new_playlist:
        stats['new_playlists'] += 1
        logger.info(f"Added new playlist: {playlist_name}")
      else:
        stats['updated_playlists'] += 1
        logger.info(f"Updated playlist: {playlist_name}")

      # Skip track sync if not a full sync and playlist exists
      if not full_sync and not is_new_playlist:
        logger.info(
          f"Skipping tracks for playlist {playlist_name} (not a full sync)"
        )
        continue

      # Get playlist tracks
      playlist_tracks = self.spotify_client.get_playlist_tracks(playlist_id)
      logger.info(
        f"Found {len(playlist_tracks)} tracks in playlist {playlist_name}"
      )

      # Sync each track
      for i, item in enumerate(playlist_tracks):
        track = item['track']
        if not track:   # Skip local tracks or other invalid tracks
          continue

        # Check if track exists in database
        db_track = self.db_manager.get_track_by_spotify_id(track['id'])
        is_new_track = db_track is None

        # Add or update track in database
        track_data = {
          'spotify_id':
            track['id'],
          'name':
            track['name'],
          'artist':
            track['artists'][0]['name'] if track['artists'] else 'Unknown',
          'album':
            track['album']['name'] if track['album'] else None,
          'duration_ms':
            track['duration_ms'],
          'popularity':
            track.get('popularity', 0),
        }

        # Only set added_at for new tracks
        if is_new_track and 'added_at' in item:
          try:
            added_at = datetime.strptime(
              item['added_at'], '%Y-%m-%dT%H:%M:%SZ'
            )
            track_data['added_at'] = added_at
          except (ValueError, TypeError):
            pass

        db_track = self.db_manager.add_track(track_data)

        if is_new_track:
          stats['new_tracks'] += 1
        else:
          stats['updated_tracks'] += 1

        # Add track to playlist
        position = i
        added_at = None
        if 'added_at' in item:
          try:
            added_at = datetime.strptime(
              item['added_at'], '%Y-%m-%dT%H:%M:%SZ'
            )
          except (ValueError, TypeError):
            pass

        self.db_manager.add_track_to_playlist(
          playlist_id=db_playlist.id,
          track_id=db_track.id,
          position=position,
          added_at=added_at
        )

      stats['tracks_synced'] += len(playlist_tracks)
      stats['playlists_synced'] += 1

    logger.info(f"Spotify sync complete: {stats}")
    return stats

  def sync_lastfm_history(
    self, days: int = 30, username: Optional[str] = None
  ) -> Dict[str, Any]:
    """
        Sync listening history from Last.fm.

        Args:
            days: Number of days of history to sync
            username: Last.fm username (defaults to configured username)

        Returns:
            Summary of the sync operation
        """
    logger.info(f"Syncing Last.fm history for the last {days} days...")

    # Authenticate with Last.fm
    self.lastfm_client.authenticate()

    # Calculate date range
    to_date = datetime.now()
    from_date = to_date - timedelta(days=days)

    # Get recent tracks
    tracks = self.lastfm_client.get_recent_tracks(
      username=username,
      limit=1000,                                     # Get a large number of tracks
      from_date=from_date,
      to_date=to_date
    )

    logger.info(f"Found {len(tracks)} tracks in Last.fm history")

    # Track sync statistics
    stats = {
      'tracks_processed': len(tracks),
      'listening_events_added': 0,
      'new_tracks_added': 0,
      'tracks_matched': 0,
      'tracks_not_matched': 0,
    }

    # Process each track
    for track in tracks:
      # Skip tracks without timestamp
      if not track['timestamp']:
        continue

      artist = track['artist']
      title = track['title']
      played_at = track['played_at']

      # Try to find matching track in database
      session = self.db_manager.get_session()
      try:
        # First, try exact match
        from mkplaylist.database.models import Track
        db_track = session.query(Track).filter(
          Track.artist == artist, Track.name == title
        ).first()

        # If not found, try case-insensitive match
        if not db_track:
          db_track = session.query(Track).filter(
            Track.artist.ilike(f"%{artist}%"), Track.name.ilike(f"%{title}%")
          ).first()

        if db_track:
          # Track found, add listening event
          stats['tracks_matched'] += 1
          self.db_manager.add_listening_event(
            track_id=db_track.id, played_at=played_at, source="lastfm"
          )
          stats['listening_events_added'] += 1
        else:
          # Track not found, create new track
          stats['tracks_not_matched'] += 1
          track_data = {
            'name': title,
            'artist': artist,
            'album': track.get('album'),
            'last_played_at': played_at,
            'play_count': 1,
          }
          db_track = self.db_manager.add_track(track_data)
          stats['new_tracks_added'] += 1

          # Add listening event
          self.db_manager.add_listening_event(
            track_id=db_track.id, played_at=played_at, source="lastfm"
          )
          stats['listening_events_added'] += 1
      finally:
        session.close()

    logger.info(f"Last.fm sync complete: {stats}")
    return stats

  def sync_all(
    self,
    full_sync: bool = False,
    days: int = 30,
    spotify_only: bool = False,
    lastfm_only: bool = False
  ) -> Dict[str, Any]:
    """
        Sync all data from Spotify and Last.fm.

        Args:
            full_sync: Whether to perform a full Spotify sync
            days: Number of days of Last.fm history to sync
            spotify_only: Only sync Spotify data
            lastfm_only: Only sync Last.fm data

        Returns:
            Summary of the sync operation
        """
    stats = {}

    if not lastfm_only:
      spotify_stats = self.sync_spotify_playlists(full_sync=full_sync)
      stats['spotify'] = spotify_stats

    if not spotify_only:
      lastfm_stats = self.sync_lastfm_history(days=days)
      stats['lastfm'] = lastfm_stats

    return stats
