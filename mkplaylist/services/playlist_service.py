"""
Playlist service for mkplaylist.

This module provides a service for generating playlists based on criteria.
"""

# Starfleet Protocols
import logging

from typing import Any
from typing import Dict
from typing import List
from typing import Optional

# Engineering Core Modules
from mkplaylist.api.spotify_client import SpotifyClient
from mkplaylist.database.db_manager import DatabaseManager
from mkplaylist.services.query_parser import QueryParser

logger = logging.getLogger(__name__)


class PlaylistService:

    """Service for generating playlists based on criteria."""

    def __init__(
        self,
        db_manager: Optional[DatabaseManager] = None,
        spotify_client: Optional[SpotifyClient] = None,
        query_parser: Optional[QueryParser] = None,
    ):
        """
        Initialize the playlist service.

        Args:
            db_manager: Database manager instance
            spotify_client: Spotify client instance
            query_parser: Query parser instance
        """
        self.db_manager = db_manager or DatabaseManager()
        self.spotify_client = spotify_client or SpotifyClient()
        self.query_parser = query_parser or QueryParser()

    def create_playlist(
        self,
        name: str,
        criteria: str,
        description: Optional[str] = None,
        public: bool = False,
        collaborative: bool = False,
        replace: bool = False,
        limit: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        Create or update a Spotify playlist based on criteria.

        Args:
            name: Name for the playlist
            criteria: Custom criteria string for selecting tracks
            description: Optional description for the playlist
            public: Whether the playlist should be public
            collaborative: Whether the playlist should be collaborative
            replace: Whether to replace all tracks in the playlist
            limit: Maximum number of tracks to include

        Returns:
            Summary of the operation
        """
        logger.info(f"Creating playlist '{name}' with criteria: {criteria}")

        # Parse criteria
        parsed_criteria = self.query_parser.parse(criteria)
        logger.info(f"Parsed criteria: {parsed_criteria}")

        # Apply global limit if specified
        if limit is not None:
            parsed_criteria["limit"] = limit

        # Get tracks matching criteria
        tracks = self.get_tracks_by_criteria(parsed_criteria)
        logger.info(f"Found {len(tracks)} tracks matching criteria")

        if not tracks:
            logger.warning("No tracks found matching criteria")
            return {
                "success": False,
                "error": "No tracks found matching criteria",
                "name": name,
                "criteria": criteria,
                "tracks_found": 0,
            }

        # Authenticate with Spotify
        self.spotify_client.authenticate()

        # Check if playlist already exists
        existing_playlist = None
        playlists = self.spotify_client.get_user_playlists()
        for playlist in playlists:
            if playlist["name"] == name:
                existing_playlist = playlist
                break

        # Create or update playlist
        if existing_playlist:
            playlist_id = existing_playlist["id"]
            logger.info(f"Updating existing playlist: {name} ({playlist_id})")

            # Get track URIs
            track_uris = [
                f"spotify:track:{track.spotify_id}"
                for track in tracks
                if track.spotify_id
            ]

            # Replace or add tracks
            if replace:
                self.spotify_client.replace_playlist_tracks(playlist_id, track_uris)
            else:
                self.spotify_client.add_tracks_to_playlist(playlist_id, track_uris)

            # Update playlist details if needed
            if description or collaborative:
                # Unfortunately, Spotipy doesn't have a direct method to update playlist details
                # We would need to use the raw API for this
                pass

            result = {
                "success": True,
                "playlist_id": playlist_id,
                "name": name,
                "criteria": criteria,
                "tracks_added": len(track_uris),
                "replaced": replace,
                "created": False,
            }
        else:
            # Create new playlist
            logger.info(f"Creating new playlist: {name}")
            playlist = self.spotify_client.create_playlist(
                name=name,
                description=description
                or f"Created by mkplaylist with criteria: {criteria}",
                public=public,
            )

            playlist_id = playlist["id"]

            # Get track URIs
            track_uris = [
                f"spotify:track:{track.spotify_id}"
                for track in tracks
                if track.spotify_id
            ]

            # Add tracks
            self.spotify_client.add_tracks_to_playlist(playlist_id, track_uris)

            result = {
                "success": True,
                "playlist_id": playlist_id,
                "name": name,
                "criteria": criteria,
                "tracks_added": len(track_uris),
                "replaced": False,
                "created": True,
            }

        logger.info(f"Playlist operation complete: {result}")
        return result

    def get_tracks_by_criteria(self, criteria: Dict[str, Any]) -> List[Any]:
        """
        Get tracks matching the given criteria.

        Args:
            criteria: Dictionary of criteria to filter tracks

        Returns:
            List of Track objects matching the criteria
        """
        # If there are multiple criteria, we need to handle them separately
        if "combined_criteria" in criteria:
            combined_results = []

            for sub_criteria in criteria["combined_criteria"]:
                # Get tracks for each sub-criteria
                tracks = self.db_manager.get_tracks_by_criteria(sub_criteria)
                combined_results.extend(tracks)

            # Remove duplicates
            unique_tracks = {}
            for track in combined_results:
                if track.id not in unique_tracks:
                    unique_tracks[track.id] = track

            tracks = list(unique_tracks.values())

            # Apply global limit if specified
            if "limit" in criteria and criteria["limit"] is not None:
                tracks = tracks[: criteria["limit"]]

            return tracks
        else:
            # Single criteria
            return self.db_manager.get_tracks_by_criteria(criteria)

    def list_playlists(
        self, format: str = "table", sort: str = "updated"
    ) -> List[Dict[str, Any]]:
        """
        List all playlists that have been created or updated by mkplaylist.

        Args:
            format: Output format ('table', 'json', 'csv')
            sort: Sort order ('name', 'date', 'updated')

        Returns:
            List of playlist information
        """
        # Authenticate with Spotify
        self.spotify_client.authenticate()

        # Get user playlists
        playlists = self.spotify_client.get_user_playlists()

        # Format playlist information
        result = []
        for playlist in playlists:
            # Get track count
            track_count = playlist["tracks"]["total"]

            # Format playlist info
            playlist_info = {
                "id": playlist["id"],
                "name": playlist["name"],
                "description": playlist.get("description", ""),
                "owner": playlist["owner"]["id"],
                "public": playlist.get("public", False),
                "collaborative": playlist.get("collaborative", False),
                "tracks": track_count,
                "url": playlist["external_urls"].get("spotify", ""),
            }
            result.append(playlist_info)

        # Sort results
        if sort == "name":
            result.sort(key=lambda x: x["name"])
        elif sort == "date":
            # We don't have creation date from Spotify API
            pass
        elif sort == "updated":
            # We don't have update date from Spotify API
            pass

        return result
