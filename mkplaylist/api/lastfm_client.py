"""
Last.fm API client for mkplaylist.

This module provides a client for interacting with the Last.fm API.
"""

# Starfleet Protocols
import logging

from typing import Any, Dict, List, Optional
from datetime import datetime

# Non-Federation Tech
import pylast

# Engineering Core Modules
from mkplaylist import config

logger = logging.getLogger(__name__)


class LastFmClient:

    """Client for interacting with the Last.fm API."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        api_secret: Optional[str] = None,
        username: Optional[str] = None,
    ):
        """
        Initialize the Last.fm client.

        Args:
            api_key: Last.fm API key (defaults to config)
            api_secret: Last.fm API secret (defaults to config)
            username: Last.fm username (defaults to config)
        """
        self.api_key = api_key or config.LASTFM_API_KEY
        self.api_secret = api_secret or config.LASTFM_API_SECRET
        self.username = username or config.LASTFM_USERNAME
        self.network = None

    def authenticate(self) -> None:
        """Authenticate with the Last.fm API."""
        self.network = pylast.LastFMNetwork(
            api_key=self.api_key, api_secret=self.api_secret
        )
        logger.info("Authenticated with Last.fm API")

    def _ensure_authenticated(self) -> None:
        """Ensure the client is authenticated."""
        if not self.network:
            self.authenticate()

    def get_user(self, username: Optional[str] = None) -> pylast.User:
        """
        Get a Last.fm user.

        Args:
            username: The username (defaults to the configured username)

        Returns:
            The User object
        """
        self._ensure_authenticated()
        return self.network.get_user(username or self.username)

    def get_recent_tracks(
        self,
        username: Optional[str] = None,
        limit: int = 50,
        from_date: Optional[datetime] = None,
        to_date: Optional[datetime] = None,
    ) -> List[Dict[str, Any]]:
        """
        Get a user's recently played tracks.

        Args:
            username: The username (defaults to the configured username)
            limit: Maximum number of tracks to return
            from_date: Start date for the range
            to_date: End date for the range

        Returns:
            List of track objects
        """
        self._ensure_authenticated()

        user = self.get_user(username)

        # Convert dates to timestamps if provided
        from_timestamp = int(from_date.timestamp()) if from_date else None
        to_timestamp = int(to_date.timestamp()) if to_date else None

        # Get recent tracks
        raw_tracks = user.get_recent_tracks(
            limit=limit, time_from=from_timestamp, time_to=to_timestamp
        )

        # Convert to a more usable format
        tracks = []
        for track in raw_tracks:
            track_dict = {
                "artist": track.track.artist.name,
                "title": track.track.title,
                "album": track.album,
                "timestamp": int(track.timestamp) if track.timestamp else None,
                "played_at": datetime.fromtimestamp(int(track.timestamp))
                if track.timestamp
                else None,
                "url": track.track.get_url(),
            }
            tracks.append(track_dict)

        return tracks

    def get_top_tracks(
        self, username: Optional[str] = None, period: str = "overall", limit: int = 50
    ) -> List[Dict[str, Any]]:
        """
        Get a user's top tracks.

        Args:
            username: The username (defaults to the configured username)
            period: Time period ('overall', '7day', '1month', '3month', '6month', '12month')
            limit: Maximum number of tracks to return

        Returns:
            List of track objects
        """
        self._ensure_authenticated()

        user = self.get_user(username)

        # Get top tracks
        raw_tracks = user.get_top_tracks(period=period, limit=limit)

        # Convert to a more usable format
        tracks = []
        for track_item in raw_tracks:
            track = track_item.item
            track_dict = {
                "artist": track.artist.name,
                "title": track.title,
                "weight": track_item.weight,  # Play count
                "url": track.get_url(),
            }
            tracks.append(track_dict)

        return tracks

    def get_track_info(
        self, artist: str, track: str, username: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get detailed information about a track.

        Args:
            artist: The artist name
            track: The track name
            username: The username for personalized data (defaults to the configured username)

        Returns:
            Track information
        """
        self._ensure_authenticated()

        track_obj = self.network.get_track(artist, track)

        # Get user playcount if username is provided
        user_playcount = None
        if username or self.username:
            user = self.get_user(username)
            try:
                user_playcount = track_obj.get_userplaycount(user)
            except pylast.WSError:
                user_playcount = 0

        # Get track info
        try:
            track_info = track_obj.get_info()

            # Convert to a more usable format
            info = {
                "artist": artist,
                "title": track,
                "album": track_info.get("album"),
                "url": track_obj.get_url(),
                "playcount": int(track_info.get("playcount", 0)),
                "listeners": int(track_info.get("listeners", 0)),
                "user_playcount": user_playcount,
                "tags": [tag.item.name for tag in track_obj.get_top_tags(limit=5)],
            }

            return info
        except pylast.WSError as e:
            logger.error(f"Error getting track info for {artist} - {track}: {e}")
            return {
                "artist": artist,
                "title": track,
                "error": str(e),
            }

    def scrobble_track(
        self, artist: str, track: str, timestamp: Optional[datetime] = None
    ) -> bool:
        """
        Scrobble a track (mark as played).

        Args:
            artist: The artist name
            track: The track name
            timestamp: When the track was played (defaults to now)

        Returns:
            True if successful, False otherwise
        """
        self._ensure_authenticated()

        if not self.username:
            logger.error("Cannot scrobble without a username")
            return False

        # Get timestamp
        if timestamp is None:
            timestamp = datetime.now()

        # Scrobble the track
        try:
            self.network.scrobble(
                artist=artist, title=track, timestamp=int(timestamp.timestamp())
            )
            logger.info(f"Scrobbled track: {artist} - {track}")
            return True
        except pylast.WSError as e:
            logger.error(f"Error scrobbling track {artist} - {track}: {e}")
            return False

    def get_similar_tracks(
        self, artist: str, track: str, limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Get tracks similar to the given track.

        Args:
            artist: The artist name
            track: The track name
            limit: Maximum number of tracks to return

        Returns:
            List of similar tracks
        """
        self._ensure_authenticated()

        track_obj = self.network.get_track(artist, track)

        try:
            similar = track_obj.get_similar(limit=limit)

            # Convert to a more usable format
            tracks = []
            for similar_item in similar:
                similar_track = similar_item.item
                track_dict = {
                    "artist": similar_track.artist.name,
                    "title": similar_track.title,
                    "match": similar_item.match,
                    "url": similar_track.get_url(),
                }
                tracks.append(track_dict)

            return tracks
        except pylast.WSError as e:
            logger.error(f"Error getting similar tracks for {artist} - {track}: {e}")
            return []
