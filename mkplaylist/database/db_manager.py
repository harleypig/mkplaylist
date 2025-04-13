"""
Database manager for mkplaylist.

This module provides a class for managing database operations.
"""

# Starfleet Protocols
import logging

from typing import Any
from typing import Dict
from typing import List
from typing import Optional
from datetime import datetime

# Non-Federation Tech
from sqlalchemy import desc
from sqlalchemy import func
from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from sqlalchemy.orm import sessionmaker

# Engineering Core Modules
from mkplaylist import config
from mkplaylist.database.models import Base
from mkplaylist.database.models import Track
from mkplaylist.database.models import Playlist
from mkplaylist.database.models import PlaylistTrack
from mkplaylist.database.models import ListeningHistory

logger = logging.getLogger(__name__)


class DatabaseManager:

    """Manages database operations."""

    def __init__(self, db_path=None):
        """
        Initialize the database manager.

        Args:
            db_path: Optional path to the database file. If not provided,
                     the default path from config will be used.
        """
        self.db_path = db_path or config.get_db_path()
        self.engine = create_engine(f"sqlite:///{self.db_path}")
        self.Session = sessionmaker(bind=self.engine)

    def create_tables(self):
        """Create all tables if they don't exist."""
        Base.metadata.create_all(self.engine)
        logger.info(f"Database tables created at {self.db_path}")

    def get_session(self) -> Session:
        """Get a new database session."""
        return self.Session()

    # Track operations
    def add_track(self, track_data: Dict[str, Any]) -> Track:
        """
        Add a new track or update an existing one.

        Args:
            track_data: Dictionary containing track data

        Returns:
            The added or updated Track object
        """
        session = self.get_session()
        try:
            # Check if track already exists
            spotify_id = track_data.get("spotify_id")
            if spotify_id:
                track = session.query(Track).filter_by(spotify_id=spotify_id).first()
                if track:
                    # Update existing track
                    for key, value in track_data.items():
                        if hasattr(track, key) and key != "id":
                            setattr(track, key, value)
                    logger.debug(f"Updated track: {track.name} by {track.artist}")
                else:
                    # Create new track
                    track = Track(**track_data)
                    session.add(track)
                    logger.debug(f"Added new track: {track.name} by {track.artist}")
            else:
                # Create new track without Spotify ID
                track = Track(**track_data)
                session.add(track)
                logger.debug(
                    f"Added new track without Spotify ID: {track.name} by {track.artist}"
                )

            session.commit()
            return track
        except SQLAlchemyError as e:
            session.rollback()
            logger.error(f"Error adding track: {e}")
            raise
        finally:
            session.close()

    def get_track_by_spotify_id(self, spotify_id: str) -> Optional[Track]:
        """
        Get a track by its Spotify ID.

        Args:
            spotify_id: The Spotify ID of the track

        Returns:
            The Track object if found, None otherwise
        """
        session = self.get_session()
        try:
            return session.query(Track).filter_by(spotify_id=spotify_id).first()
        finally:
            session.close()

    def get_tracks_by_criteria(self, criteria: Dict[str, Any]) -> List[Track]:
        """
        Get tracks matching the given criteria.

        Args:
            criteria: Dictionary of criteria to filter tracks

        Returns:
            List of Track objects matching the criteria
        """
        session = self.get_session()
        try:
            query = session.query(Track)

            # Apply filters based on criteria
            if "artist" in criteria:
                query = query.filter(Track.artist == criteria["artist"])
            if "album" in criteria:
                query = query.filter(Track.album == criteria["album"])
            if "added_after" in criteria:
                query = query.filter(Track.added_at >= criteria["added_after"])
            if "played_after" in criteria:
                query = query.filter(Track.last_played_at >= criteria["played_after"])

            # Apply sorting
            if criteria.get("sort_by") == "added_at":
                query = query.order_by(desc(Track.added_at))
            elif criteria.get("sort_by") == "last_played_at":
                query = query.order_by(desc(Track.last_played_at))
            elif criteria.get("sort_by") == "play_count":
                query = query.order_by(desc(Track.play_count))

            # Apply limit
            if "limit" in criteria:
                query = query.limit(criteria["limit"])

            return query.all()
        finally:
            session.close()

    # Playlist operations
    def add_playlist(self, playlist_data: Dict[str, Any]) -> Playlist:
        """
        Add a new playlist or update an existing one.

        Args:
            playlist_data: Dictionary containing playlist data

        Returns:
            The added or updated Playlist object
        """
        session = self.get_session()
        try:
            # Check if playlist already exists
            spotify_id = playlist_data.get("spotify_id")
            if spotify_id:
                playlist = (
                    session.query(Playlist).filter_by(spotify_id=spotify_id).first()
                )
                if playlist:
                    # Update existing playlist
                    for key, value in playlist_data.items():
                        if hasattr(playlist, key) and key != "id":
                            setattr(playlist, key, value)
                    logger.debug(f"Updated playlist: {playlist.name}")
                else:
                    # Create new playlist
                    playlist = Playlist(**playlist_data)
                    session.add(playlist)
                    logger.debug(f"Added new playlist: {playlist.name}")
            else:
                # Create new playlist without Spotify ID
                playlist = Playlist(**playlist_data)
                session.add(playlist)
                logger.debug(f"Added new playlist without Spotify ID: {playlist.name}")

            session.commit()
            return playlist
        except SQLAlchemyError as e:
            session.rollback()
            logger.error(f"Error adding playlist: {e}")
            raise
        finally:
            session.close()

    def get_playlist_by_spotify_id(self, spotify_id: str) -> Optional[Playlist]:
        """
        Get a playlist by its Spotify ID.

        Args:
            spotify_id: The Spotify ID of the playlist

        Returns:
            The Playlist object if found, None otherwise
        """
        session = self.get_session()
        try:
            return session.query(Playlist).filter_by(spotify_id=spotify_id).first()
        finally:
            session.close()

    def add_track_to_playlist(
        self,
        playlist_id: int,
        track_id: int,
        position: Optional[int] = None,
        added_at: Optional[datetime] = None,
    ) -> PlaylistTrack:
        """
        Add a track to a playlist.

        Args:
            playlist_id: ID of the playlist
            track_id: ID of the track
            position: Optional position in the playlist
            added_at: Optional timestamp when the track was added

        Returns:
            The created PlaylistTrack object
        """
        session = self.get_session()
        try:
            # Check if the track is already in the playlist
            playlist_track = (
                session.query(PlaylistTrack)
                .filter_by(playlist_id=playlist_id, track_id=track_id)
                .first()
            )

            if playlist_track:
                # Update existing playlist track
                if position is not None:
                    playlist_track.position = position
                if added_at is not None:
                    playlist_track.added_at = added_at
                logger.debug(
                    f"Updated track position in playlist: {playlist_id}, track: {track_id}"
                )
            else:
                # Create new playlist track
                playlist_track = PlaylistTrack(
                    playlist_id=playlist_id,
                    track_id=track_id,
                    position=position,
                    added_at=added_at or datetime.utcnow(),
                )
                session.add(playlist_track)
                logger.debug(
                    f"Added track to playlist: {playlist_id}, track: {track_id}"
                )

            session.commit()
            return playlist_track
        except SQLAlchemyError as e:
            session.rollback()
            logger.error(f"Error adding track to playlist: {e}")
            raise
        finally:
            session.close()

    # Listening history operations
    def add_listening_event(
        self, track_id: int, played_at: datetime, source: str = "lastfm"
    ) -> ListeningHistory:
        """
        Add a new listening event.

        Args:
            track_id: ID of the track
            played_at: When the track was played
            source: Source of the play data (default: "lastfm")

        Returns:
            The created ListeningHistory object
        """
        session = self.get_session()
        try:
            # Create new listening history entry
            history = ListeningHistory(
                track_id=track_id, played_at=played_at, source=source
            )
            session.add(history)

            # Update the track's last_played_at and play_count
            track = session.query(Track).filter_by(id=track_id).first()
            if track:
                if track.last_played_at is None or played_at > track.last_played_at:
                    track.last_played_at = played_at
                track.play_count += 1

            session.commit()
            logger.debug(
                f"Added listening event for track: {track_id}, played at: {played_at}"
            )
            return history
        except SQLAlchemyError as e:
            session.rollback()
            logger.error(f"Error adding listening event: {e}")
            raise
        finally:
            session.close()

    def get_recently_played_tracks(self, limit: int = 10) -> List[Track]:
        """
        Get the most recently played tracks.

        Args:
            limit: Maximum number of tracks to return

        Returns:
            List of Track objects
        """
        session = self.get_session()
        try:
            # Get the most recent listening event for each track
            subquery = (
                session.query(
                    ListeningHistory.track_id,
                    func.max(ListeningHistory.played_at).label("max_played_at"),
                )
                .group_by(ListeningHistory.track_id)
                .subquery()
            )

            # Join with the tracks table and order by played_at
            query = (
                session.query(Track)
                .join(subquery, Track.id == subquery.c.track_id)
                .order_by(desc(subquery.c.max_played_at))
                .limit(limit)
            )

            return query.all()
        finally:
            session.close()

    # Utility methods
    def clear_all_data(self):
        """Clear all data from the database."""
        session = self.get_session()
        try:
            session.query(ListeningHistory).delete()
            session.query(PlaylistTrack).delete()
            session.query(Track).delete()
            session.query(Playlist).delete()
            session.commit()
            logger.info("All data cleared from the database")
        except SQLAlchemyError as e:
            session.rollback()
            logger.error(f"Error clearing data: {e}")
            raise
        finally:
            session.close()
