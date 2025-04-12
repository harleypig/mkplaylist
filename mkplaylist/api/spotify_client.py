
"""
Spotify API client for mkplaylist.

This module provides a client for interacting with the Spotify API.
"""

import logging
import os
import time
from typing import Dict, List, Optional, Any, Union

import spotipy
from spotipy.oauth2 import SpotifyOAuth
from spotipy.exceptions import SpotifyException

from mkplaylist.config import MkPlaylistConfig

from mkplaylist import config

logger = logging.getLogger(__name__)


class SpotifyClient:

  """Client for interacting with the Spotify API."""

  def __init__(
    self,
    client_id: Optional[str] = None,
    client_secret: Optional[str] = None,
    redirect_uri: Optional[str] = None
  ):
    """
        Initialize the Spotify client.
        
        Args:
            client_id: Spotify client ID (defaults to config)
            client_secret: Spotify client secret (defaults to config)
            redirect_uri: Redirect URI for OAuth (defaults to config)
        """

    self.config = MkPlaylistConfig()
    self.client_id = client_id or self.config.SPOTIFY_CLIENT_ID
    self.client_secret = client_secret or self.config.SPOTIFY_CLIENT_SECRET
    self.redirect_uri = redirect_uri or self.config.SPOTIFY_REDIRECT_URI
    
    self.sp = None

  def authenticate(self, scope: Optional[str] = None) -> None:
    """
        Authenticate with the Spotify API.
        
        Args:
            scope: Optional scope string for authorization
        """
    if not scope:
      scope = (
        'user-read-private user-read-email '
        'playlist-read-private playlist-read-collaborative '
        'playlist-modify-public playlist-modify-private '
        'user-library-read'
      )


    # Use the state directory for token storage
    token_path = f"{self.config.get_state_dir()}/spotify_token.json"
    
    auth_manager = SpotifyOAuth(
      client_id=self.client_id,
      client_secret=self.client_secret,
      redirect_uri=self.redirect_uri,
      scope=scope,
      cache_path=token_path
    )
    

    self.sp = spotipy.Spotify(auth_manager=auth_manager)
    logger.info("Authenticated with Spotify API")

    # Test the connection
    try:
      self.sp.current_user()
      logger.info("Successfully connected to Spotify API")
    except SpotifyException as e:
      logger.error(f"Failed to connect to Spotify API: {e}")
      raise

  def _ensure_authenticated(self) -> None:
    """Ensure the client is authenticated."""
    if not self.sp:
      self.authenticate()

  def get_current_user(self) -> Dict[str, Any]:
    """
        Get the current user's profile.
        
        Returns:
            The user profile data
        """
    self._ensure_authenticated()
    return self.sp.current_user()

  def get_user_playlists(self, limit: int = 50) -> List[Dict[str, Any]]:
    """
        Get the current user's playlists.
        
        Args:
            limit: Maximum number of playlists to return
            
        Returns:
            List of playlist objects
        """
    self._ensure_authenticated()

    playlists = []
    results = self.sp.current_user_playlists(limit=limit)

    while results:
      playlists.extend(results['items'])
      if results['next']:
        results = self.sp.next(results)
      else:
        results = None

    return playlists

  def get_playlist(self, playlist_id: str) -> Dict[str, Any]:
    """
        Get a specific playlist.
        
        Args:
            playlist_id: The Spotify ID of the playlist
            
        Returns:
            The playlist object
        """
    self._ensure_authenticated()
    return self.sp.playlist(playlist_id)

  def get_playlist_tracks(self, playlist_id: str) -> List[Dict[str, Any]]:
    """
        Get all tracks in a playlist.
        
        Args:
            playlist_id: The Spotify ID of the playlist
            
        Returns:
            List of track objects
        """
    self._ensure_authenticated()

    tracks = []
    results = self.sp.playlist_items(playlist_id)

    while results:
      tracks.extend(results['items'])
      if results['next']:
        results = self.sp.next(results)
      else:
        results = None

    return tracks



  def create_playlist(
    self,
    name: str,
    description: str = "",
    public: bool = False
  ) -> Dict[str, Any]:
    """
        Create a new playlist.
        
        Args:
            name: The name of the playlist
            description: Optional description for the playlist
            public: Whether the playlist should be public
            
        Returns:
            The created playlist object
        """
    self._ensure_authenticated()

    user_id = self.get_current_user()['id']
    return self.sp.user_playlist_create(
      user=user_id, name=name, public=public, description=description
    )

  def add_tracks_to_playlist(self, playlist_id: str,
                             track_uris: List[str]) -> Dict[str, Any]:
    """
        Add tracks to a playlist.
        
        Args:
            playlist_id: The Spotify ID of the playlist
            track_uris: List of Spotify track URIs to add
            
        Returns:
            The API response
        """
    self._ensure_authenticated()

    # Spotify API has a limit of 100 tracks per request
    responses = []
    for i in range(0, len(track_uris), 100):
      chunk = track_uris[i:i + 100]
      response = self.sp.playlist_add_items(playlist_id, chunk)
      responses.append(response)

      # Avoid rate limiting
      if i + 100 < len(track_uris):
        time.sleep(1)

    return responses[-1] if responses else None

  def replace_playlist_tracks(self, playlist_id: str,
                              track_uris: List[str]) -> Dict[str, Any]:
    """
        Replace all tracks in a playlist.
        
        Args:
            playlist_id: The Spotify ID of the playlist
            track_uris: List of Spotify track URIs to add
            
        Returns:
            The API response
        """
    self._ensure_authenticated()

    # First, replace with the first 100 tracks (or fewer)
    first_chunk = track_uris[:100]
    response = self.sp.playlist_replace_items(playlist_id, first_chunk)

    # If there are more tracks, add them
    if len(track_uris) > 100:
      remaining_tracks = track_uris[100:]
      self.add_tracks_to_playlist(playlist_id, remaining_tracks)

    return response

  def remove_tracks_from_playlist(
    self, playlist_id: str, track_uris: List[str]
  ) -> Dict[str, Any]:
    """
        Remove tracks from a playlist.
        
        Args:
            playlist_id: The Spotify ID of the playlist
            track_uris: List of Spotify track URIs to remove
            
        Returns:
            The API response
        """
    self._ensure_authenticated()

    # Spotify API has a limit of 100 tracks per request
    responses = []
    for i in range(0, len(track_uris), 100):
      chunk = track_uris[i:i + 100]
      response = self.sp.playlist_remove_all_occurrences_of_items(
        playlist_id, chunk
      )
      responses.append(response)

      # Avoid rate limiting
      if i + 100 < len(track_uris):
        time.sleep(1)

    return responses[-1] if responses else None

  def search_tracks(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
    """
        Search for tracks.
        
        Args:
            query: Search query
            limit: Maximum number of tracks to return
            
        Returns:
            List of track objects
        """
    self._ensure_authenticated()

    results = self.sp.search(q=query, type='track', limit=limit)
    return results['tracks']['items']

  def get_track(self, track_id: str) -> Dict[str, Any]:
    """
        Get a specific track.
        
        Args:
            track_id: The Spotify ID of the track
            
        Returns:
            The track object
        """
    self._ensure_authenticated()
    return self.sp.track(track_id)

  def get_several_tracks(self, track_ids: List[str]) -> List[Dict[str, Any]]:
    """
        Get several tracks.
        
        Args:
            track_ids: List of Spotify track IDs
            
        Returns:
            List of track objects
        """
    self._ensure_authenticated()

    # Spotify API has a limit of 50 tracks per request
    tracks = []
    for i in range(0, len(track_ids), 50):
      chunk = track_ids[i:i + 50]
      results = self.sp.tracks(chunk)
      tracks.extend(results['tracks'])

      # Avoid rate limiting
      if i + 50 < len(track_ids):
        time.sleep(1)

    return tracks

