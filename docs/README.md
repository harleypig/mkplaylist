
# mkplaylist Documentation

This directory contains documentation for the mkplaylist application.

## Project Overview

mkplaylist is a Python application that integrates with Spotify and Last.fm
APIs to create and manage playlists based on custom criteria. The application
allows users to:

- Sync data from Spotify playlists to a local SQLite database
- Fetch listening history from Last.fm and match it to tracks
- Create or update Spotify playlists based on flexible, user-defined criteria

The primary goal is to combine data from both services to create dynamic
playlists that can be based on criteria like "recently added songs" and "last
played songs".

## Key Features

- **Data Synchronization**: Periodically sync Spotify playlists and Last.fm listening history to a local SQLite database
- **Custom Playlist Generation**: Create playlists using natural language-like criteria
- **Command-line Interface**: Simple CLI for managing playlists and data synchronization

## Technology Stack

- **Programming Language**: Python
- **Database**: SQLite
- **API Integrations**:
  - Spotify API (using Spotipy library)
  - Last.fm API (using pylast library)
- **ORM**: SQLAlchemy for database operations
- **CLI Framework**: Click for command-line interface

## CLI Design

```
mkplaylist sync                                  # Sync data from Spotify and Last.fm
mkplaylist create <alias_name> '<custom_criteria>'  # Create playlist with custom criteria
mkplaylist list                                  # List available playlists
```

## Directory Structure

- `user/` - Documentation for end users
  - `installation.md` - Installation instructions
  - `getting_started.md` - Getting started guide
  - `commands.md` - Command reference
  - `examples.md` - Example usage

- `dev/` - Documentation for developers
  - `architecture.md` - Architecture overview
  - `api_integration.md` - API integration details
  - `database.md` - Database schema
  - `contributing.md` - Contributing guidelines

## Project Structure

The main project structure is organized as follows:

```
harleypig/mkplaylist/
├── mkplaylist/            # Main package code
│   ├── __init__.py        # Package initialization
│   ├── config.py          # Configuration and API credentials
│   ├── database/          # Database models and operations
│   ├── api/               # API clients for Spotify and Last.fm
│   ├── services/          # Business logic services
│   └── cli.py             # Command-line interface
├── docs/                  # Documentation
├── tests/                 # Test suite
├── setup.py               # Package installation configuration
├── requirements.txt       # Dependencies
└── .env.example           # Example environment variables
```

## Database Schema

The SQLite database uses the following schema:

- `mkplaylist_tracks`: Store track information (id, name, artist, album, etc.)
- `mkplaylist_playlists`: Store playlist metadata (id, name, description)
- `mkplaylist_playlist_tracks`: Junction table linking tracks to playlists (with added_date)
- `mkplaylist_listening_history`: Store when tracks were played (track_id, played_at)

## Getting Started

For installation and usage instructions, please refer to the user
documentation in the `user/` directory.

For development information, please refer to the developer documentation in
the `dev/` directory.
