"""
Database models for mkplaylist.

This module defines the SQLAlchemy ORM models for the database tables.
"""

# Starfleet Protocols
from datetime import datetime

# Non-Federation Tech
from sqlalchemy import (
  Column, String, Boolean, Integer, DateTime, ForeignKey, UniqueConstraint,
)
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Track(Base):

  """Model representing a music track."""

  __tablename__ = "mkplaylist_tracks"

  id = Column(Integer, primary_key=True)
  spotify_id = Column(String, unique=True, index=True)
  name = Column(String, nullable=False)
  artist = Column(String, nullable=False)
  album = Column(String)
  duration_ms = Column(Integer)
  popularity = Column(Integer)
  added_at = Column(DateTime, default=datetime.utcnow, index=True)
  last_played_at = Column(DateTime, index=True)
  play_count = Column(Integer, default=0)
  created_at = Column(DateTime, default=datetime.utcnow)
  updated_at = Column(
    DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
  )

  # Relationships
  playlists = relationship(
    "Playlist",
    secondary="mkplaylist_playlist_tracks",
    back_populates="tracks"
  )
  listening_history = relationship("ListeningHistory", back_populates="track")

  def __repr__(self):
    return f"<Track(id={self.id}, name='{self.name}', artist='{self.artist}')>"


class Playlist(Base):

  """Model representing a playlist."""

  __tablename__ = "mkplaylist_playlists"

  id = Column(Integer, primary_key=True)
  spotify_id = Column(String, unique=True, index=True)
  name = Column(String, nullable=False, index=True)
  description = Column(String)
  owner = Column(String)
  is_public = Column(Boolean, default=False)
  created_at = Column(DateTime, default=datetime.utcnow)
  updated_at = Column(
    DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
  )

  # Relationships
  tracks = relationship(
    "Track",
    secondary="mkplaylist_playlist_tracks",
    back_populates="playlists"
  )
  playlist_tracks = relationship("PlaylistTrack", back_populates="playlist")

  def __repr__(self):
    return f"<Playlist(id={self.id}, name='{self.name}')>"


class PlaylistTrack(Base):

  """Junction model linking tracks to playlists."""

  __tablename__ = "mkplaylist_playlist_tracks"

  id = Column(Integer, primary_key=True)
  playlist_id = Column(
    Integer, ForeignKey("mkplaylist_playlists.id"), index=True
  )
  track_id = Column(Integer, ForeignKey("mkplaylist_tracks.id"), index=True)
  position = Column(Integer)
  added_at = Column(DateTime, default=datetime.utcnow, index=True)
  created_at = Column(DateTime, default=datetime.utcnow)

  # Relationships
  playlist = relationship("Playlist", back_populates="playlist_tracks")
  track = relationship("Track")

  # Constraints
  __table_args__ = (
    UniqueConstraint("playlist_id", "track_id", name="uq_playlist_track"),
  )

  def __repr__(self):
    return (
      f"<PlaylistTrack(playlist_id={self.playlist_id}, track_id={self.track_id})>"
    )


class ListeningHistory(Base):

  """Model representing a track play event."""

  __tablename__ = "mkplaylist_listening_history"

  id = Column(Integer, primary_key=True)
  track_id = Column(Integer, ForeignKey("mkplaylist_tracks.id"), index=True)
  played_at = Column(DateTime, nullable=False, index=True)
  source = Column(String, default="lastfm")
  created_at = Column(DateTime, default=datetime.utcnow)

  # Relationships
  track = relationship("Track", back_populates="listening_history")

  def __repr__(self):
    return f"<ListeningHistory(track_id={self.track_id}, played_at='{self.played_at}')>"
