# Database Schema

This document provides detailed information about the database schema used in
the mkplaylist application.

## Overview

mkplaylist uses SQLite as its database engine, with SQLAlchemy as the ORM
(Object-Relational Mapping) layer. The database stores information about
tracks, playlists, and listening history, combining data from both Spotify and
Last.fm.

## Database File

By default, the database is stored in a file named `mkplaylist.db` in the
user's data directory:

- Linux: `~/.local/share/mkplaylist/mkplaylist.db`
- macOS: `~/Library/Application Support/mkplaylist/mkplaylist.db`
- Windows: `C:\Users\<username>\AppData\Local\mkplaylist\mkplaylist.db`

This location can be overridden using the `MKPLAYLIST_DB_PATH` environment
variable.

## Directory Structure

mkplaylist follows the XDG Base Directory Specification for organizing its
files across different operating systems. This provides a standardized way to
store application data, configuration, cache, and state files.

### XDG Base Directory Specification

The XDG Base Directory Specification defines several environment variables
that determine where applications should store different types of files:

- `XDG_DATA_HOME`: For user-specific data files (~/.local/share/ by default on Linux)
- `XDG_CONFIG_HOME`: For user-specific configuration files (~/.config/ by default on Linux)
- `XDG_CACHE_HOME`: For non-essential data files (~/.cache/ by default on Linux)
- `XDG_STATE_HOME`: For user-specific state data (~/.local/state/ by default on Linux)

### Directory Functions

The application provides several functions in `mkplaylist/config.py` to handle
directory paths according to the XDG specification:

#### `get_data_dir()`

Returns the path to the data directory for storing persistent application data like the database.

```python
def get_data_dir() -> Path:
    """Get the data directory for the application."""
    if os.name == 'nt':  # Windows
        base_dir = Path(os.environ.get('APPDATA', '')) / 'mkplaylist'
    else:  # Unix/Linux/Mac
        base_dir = Path(
            os.environ.get('XDG_DATA_HOME',
                           Path.home() / '.local' / 'share')
        ) / 'mkplaylist'

    # Create directory if it doesn't exist
    base_dir.mkdir(parents=True, exist_ok=True)
    return base_dir
```

#### `get_config_dir()`

Returns the path to the configuration directory for storing application settings.

```python
def get_config_dir() -> Path:
    """
    Get the configuration directory for the application.

    Following XDG Base Directory Specification:
    - On Unix/Linux/Mac: $XDG_CONFIG_HOME/mkplaylist (~/.config/mkplaylist by default)
    - On Windows: %APPDATA%\mkplaylist\config

    Returns:
        Path: The configuration directory path
    """
    if os.name == 'nt':  # Windows
        base_dir = Path(os.environ.get('APPDATA', '')) / 'mkplaylist' / 'config'
    else:  # Unix/Linux/Mac
        base_dir = Path(
            os.environ.get('XDG_CONFIG_HOME',
                           Path.home() / '.config')
        ) / 'mkplaylist'

    # Create directory if it doesn't exist
    base_dir.mkdir(parents=True, exist_ok=True)
    return base_dir
```

#### `get_cache_dir()`

Returns the path to the cache directory for storing non-essential data that can be regenerated.

```python
def get_cache_dir() -> Path:
    """
    Get the cache directory for the application.

    Following XDG Base Directory Specification:
    - On Unix/Linux/Mac: $XDG_CACHE_HOME/mkplaylist (~/.cache/mkplaylist by default)
    - On Windows: %LOCALAPPDATA%\mkplaylist\cache

    Returns:
        Path: The cache directory path
    """
    if os.name == 'nt':  # Windows
        base_dir = Path(os.environ.get('LOCALAPPDATA', '')) / 'mkplaylist' / 'cache'
    else:  # Unix/Linux/Mac
        base_dir = Path(
            os.environ.get('XDG_CACHE_HOME',
                           Path.home() / '.cache')
        ) / 'mkplaylist'

    # Create directory if it doesn't exist
    base_dir.mkdir(parents=True, exist_ok=True)
    return base_dir
```

#### `get_state_dir()`

Returns the path to the state directory for storing persistent application state data like authentication tokens.

```python
def get_state_dir() -> Path:
    """
    Get the state directory for the application.

    Following XDG Base Directory Specification:
    - On Unix/Linux/Mac: $XDG_STATE_HOME/mkplaylist (~/.local/state/mkplaylist by default)
    - On Windows: %LOCALAPPDATA%\mkplaylist\state

    This directory is used for persistent application state data like authentication tokens.

    Returns:
        Path: The state directory path
    """
    if os.name == 'nt':  # Windows
        base_dir = Path(os.environ.get('LOCALAPPDATA', '')) / 'mkplaylist' / 'state'
    else:  # Unix/Linux/Mac
        base_dir = Path(
            os.environ.get('XDG_STATE_HOME',
                           Path.home() / '.local' / 'state')
        ) / 'mkplaylist'

    # Create directory if it doesn't exist
    base_dir.mkdir(parents=True, exist_ok=True)
    return base_dir
```

#### `get_db_path()`

Returns the path to the SQLite database file, with support for a custom path via environment variable.

```python
```python
def get_db_path() -> Path:
    """Get the path to the SQLite database file."""
    # Check for custom path in environment variable
    custom_path = os.environ.get('MKPLAYLIST_DB_PATH')
    if custom_path:
        return Path(custom_path)

    # Default path in data directory
    default_path = get_data_dir() / 'mkplaylist.db'




    return default_path
```

### Technical Note on XDG Environment Variables

The directory functions (`get_data_dir()`, `get_config_dir()`, `get_cache_dir()`, and `get_state_dir()`) access environment variables directly using `os.environ.get()`. This has important implications for how configuration values are loaded and applied:

1. **Timing of Environment Variable Access**: These functions read environment variables at the time they are called, not when the module is imported.

2. **`.env` File Interaction**: While the application uses `python-dotenv` to load variables from a `.env` file with `load_dotenv(override=True)`, there's a timing consideration:
   - If directory functions are called during module imports (before `load_dotenv()` is executed), they will use the original environment variables, not those from the `.env` file.
   - If directory functions are called after `load_dotenv()` has executed, they will use the environment variables as overridden by the `.env` file.

3. **Precedence Order**:
   - System environment variables provide the baseline configuration
   - Values from the `.env` file override these environment variables when loaded
   - For XDG directory settings specifically, this means that values in the `.env` file will take precedence, but only if the directory functions are called after the `.env` file is loaded

4. **Recommended Approach for Extensions**:
   - If you're extending the codebase and need reliable access to these directories, ensure that your code runs after the configuration module has been fully initialized.
   - For the most predictable behavior, access these directories through the provided functions rather than directly using environment variables.
   - If you need to customize XDG paths, setting environment variables before the application starts is the most reliable method, though `.env` file settings will work in most cases.

```

### File Locations

The application uses these directory functions to determine where to store different types of files:

| File Type | Function | Default Location (Linux) | Environment Variable |
|-----------|----------|--------------------------|----------------------|
| Database | `get_db_path()` | ~/.local/share/mkplaylist/mkplaylist.db | MKPLAYLIST_DB_PATH |
| Spotify Token | N/A (uses state dir) | ~/.local/state/mkplaylist/spotify_token.json | XDG_STATE_HOME |
| Configuration | N/A (future use) | ~/.config/mkplaylist/ | XDG_CONFIG_HOME |
| Cache | N/A (future use) | ~/.cache/mkplaylist/ | XDG_CACHE_HOME |

### Migration Strategy

The application includes migration logic to handle existing files in old locations:

1. **Database Migration**: If a database file exists in the current directory but not in the new XDG-compliant location, it will be copied to the new location.

2. **Spotify Token Migration**: If a Spotify token file exists in the old location (data directory) but not in the new location (state directory), it will be copied to the new location.

This migration strategy ensures a smooth transition for users upgrading from previous versions while maintaining backward compatibility.

### Usage Examples

Here are examples of how to use the directory functions in your code:

#### Getting the Database Path

```python
from mkplaylist import config

# Get the database path
db_path = config.get_db_path()
print(f"Database path: {db_path}")

# Use the path with SQLAlchemy
from sqlalchemy import create_engine
engine = create_engine(f"sqlite:///{db_path}")
```

#### Storing Configuration Files

```python
from mkplaylist import config
import json

# Get the configuration directory
config_dir = config.get_config_dir()
config_file = config_dir / "settings.json"

# Save configuration
settings = {"theme": "dark", "sync_interval": 3600}
with open(config_file, "w") as f:
    json.dump(settings, f)

# Load configuration
if config_file.exists():
    with open(config_file, "r") as f:
        settings = json.load(f)
```

#### Caching API Responses

```python
from mkplaylist import config
import json
import hashlib
import time

def get_cached_response(url, max_age=3600):
    # Get the cache directory
    cache_dir = config.get_cache_dir()

    # Create a cache key from the URL
    url_hash = hashlib.md5(url.encode()).hexdigest()
    cache_file = cache_dir / f"{url_hash}.json"

    # Check if cache exists and is fresh
    if cache_file.exists():
        with open(cache_file, "r") as f:
            cached_data = json.load(f)

        # Check if cache is still valid
        if time.time() - cached_data["timestamp"] < max_age:
            return cached_data["data"]

    # Cache miss or expired, fetch new data
    data = fetch_from_api(url)  # Implement this function

    # Save to cache
    with open(cache_file, "w") as f:
        json.dump({"timestamp": time.time(), "data": data}, f)

    return data
```

#### Storing Authentication State

```python
from mkplaylist import config
import json

def save_auth_token(token_data):
    # Get the state directory
    state_dir = config.get_state_dir()
    token_file = state_dir / "auth_token.json"

    # Save token data
    with open(token_file, "w") as f:
        json.dump(token_data, f)

def load_auth_token():
    # Get the state directory
    state_dir = config.get_state_dir()
    token_file = state_dir / "auth_token.json"

    # Load token data if it exists
    if token_file.exists():
        with open(token_file, "r") as f:
            return json.load(f)

    return None
```

This location can be overridden using the `MKPLAYLIST_DB_PATH` environment
variable.

## Schema Diagram

```
┌─────────────────────┐       ┌─────────────────────┐
│ mkplaylist_tracks   │       │ mkplaylist_playlists│
├─────────────────────┤       ├─────────────────────┤
│ id (PK)             │       │ id (PK)             │
│ spotify_id          │◄──┐   │ spotify_id          │
│ name                │   │   │ name                │
│ artist              │   │   │ description         │
│ album               │   │   │ owner               │
│ duration_ms         │   │   │ is_public           │
│ popularity          │   │   │ created_at          │
│ added_at            │   │   │ updated_at          │
│ last_played_at      │   │   └─────────────────────┘
│ play_count          │   │           ▲
│ created_at          │   │           │
│ updated_at          │   │           │
└─────────────────────┘   │           │
         ▲                │           │
         │                │           │
         │                │           │
┌────────┴────────────┐   │   ┌───────┴─────────────┐
│mkplaylist_listening_│   │   │mkplaylist_playlist_ │
│     history         │   │   │      tracks         │
├─────────────────────┤   │   ├─────────────────────┤
│ id (PK)             │   │   │ id (PK)             │
│ track_id (FK)       │───┘   │ playlist_id (FK)    │
│ played_at           │       │ track_id (FK)       │
│ source              │       │ position            │
│ created_at          │       │ added_at            │
└─────────────────────┘       │ created_at          │
                              └─────────────────────┘
```

## Table Definitions

### mkplaylist_tracks

Stores information about individual tracks.

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary key |
| spotify_id | TEXT | Spotify track ID (unique) |
| name | TEXT | Track name |
| artist | TEXT | Artist name |
| album | TEXT | Album name |
| duration_ms | INTEGER | Track duration in milliseconds |
| popularity | INTEGER | Spotify popularity score (0-100) |
| added_at | TIMESTAMP | When the track was first added to the database |
| last_played_at | TIMESTAMP | When the track was last played (from Last.fm) |
| play_count | INTEGER | Number of times the track has been played (from Last.fm) |
| created_at | TIMESTAMP | Record creation timestamp |
| updated_at | TIMESTAMP | Record update timestamp |

Indexes:
- `idx_tracks_spotify_id` on `spotify_id`
- `idx_tracks_name_artist` on `name` and `artist`
- `idx_tracks_added_at` on `added_at`
- `idx_tracks_last_played_at` on `last_played_at`

### mkplaylist_playlists

Stores information about playlists.

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary key |
| spotify_id | TEXT | Spotify playlist ID (unique) |
| name | TEXT | Playlist name |
| description | TEXT | Playlist description |
| owner | TEXT | Playlist owner (Spotify username) |
| is_public | BOOLEAN | Whether the playlist is public |
| created_at | TIMESTAMP | Record creation timestamp |
| updated_at | TIMESTAMP | Record update timestamp |

Indexes:
- `idx_playlists_spotify_id` on `spotify_id`
- `idx_playlists_name` on `name`

### mkplaylist_playlist_tracks

Junction table linking tracks to playlists.

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary key |
| playlist_id | INTEGER | Foreign key to mkplaylist_playlists.id |
| track_id | INTEGER | Foreign key to mkplaylist_tracks.id |
| position | INTEGER | Position of the track in the playlist |
| added_at | TIMESTAMP | When the track was added to the playlist |
| created_at | TIMESTAMP | Record creation timestamp |

Indexes:
- `idx_playlist_tracks_playlist_id` on `playlist_id`
- `idx_playlist_tracks_track_id` on `track_id`
- `idx_playlist_tracks_added_at` on `added_at`
- Unique constraint on `(playlist_id, track_id)` to prevent duplicates

### mkplaylist_listening_history

Stores information about when tracks were played.

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary key |
| track_id | INTEGER | Foreign key to mkplaylist_tracks.id |
| played_at | TIMESTAMP | When the track was played |
| source | TEXT | Source of the play data (e.g., "lastfm") |
| created_at | TIMESTAMP | Record creation timestamp |

Indexes:
- `idx_listening_history_track_id` on `track_id`
- `idx_listening_history_played_at` on `played_at`

## SQLAlchemy Models

The database schema is implemented using SQLAlchemy ORM models in
`mkplaylist/database/models.py`.

### Base Model

All models inherit from a common base class that provides common fields and
functionality:

```python
class Base(DeclarativeBase):
    """Base class for all models."""

    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
```

### Track Model

```python
class Track(Base):
    """Model representing a music track."""

    __tablename__ = "mkplaylist_tracks"

    spotify_id = Column(String, unique=True, index=True)
    name = Column(String, nullable=False)
    artist = Column(String, nullable=False)
    album = Column(String)
    duration_ms = Column(Integer)
    popularity = Column(Integer)
    added_at = Column(DateTime, default=datetime.utcnow, index=True)
    last_played_at = Column(DateTime, index=True)
    play_count = Column(Integer, default=0)

    # Relationships
    playlists = relationship("Playlist", secondary="mkplaylist_playlist_tracks", back_populates="tracks")
    listening_history = relationship("ListeningHistory", back_populates="track")
```

### Playlist Model

```python
class Playlist(Base):
    """Model representing a playlist."""

    __tablename__ = "mkplaylist_playlists"

    spotify_id = Column(String, unique=True, index=True)
    name = Column(String, nullable=False, index=True)
    description = Column(String)
    owner = Column(String)
    is_public = Column(Boolean, default=False)

    # Relationships
    tracks = relationship("Track", secondary="mkplaylist_playlist_tracks", back_populates="playlists")
    playlist_tracks = relationship("PlaylistTrack", back_populates="playlist")
```

### PlaylistTrack Model

```python
class PlaylistTrack(Base):
    """Junction model linking tracks to playlists."""

    __tablename__ = "mkplaylist_playlist_tracks"

    playlist_id = Column(Integer, ForeignKey("mkplaylist_playlists.id"), index=True)
    track_id = Column(Integer, ForeignKey("mkplaylist_tracks.id"), index=True)
    position = Column(Integer)
    added_at = Column(DateTime, default=datetime.utcnow, index=True)

    # Relationships
    playlist = relationship("Playlist", back_populates="playlist_tracks")
    track = relationship("Track")

    # Constraints
    __table_args__ = (
        UniqueConstraint("playlist_id", "track_id", name="uq_playlist_track"),
    )
```

### ListeningHistory Model

```python
class ListeningHistory(Base):
    """Model representing a track play event."""

    __tablename__ = "mkplaylist_listening_history"

    track_id = Column(Integer, ForeignKey("mkplaylist_tracks.id"), index=True)
    played_at = Column(DateTime, nullable=False, index=True)
    source = Column(String, default="lastfm")

    # Relationships
    track = relationship("Track", back_populates="listening_history")
```

## Database Operations

The `DatabaseManager` class in `mkplaylist/database/db_manager.py` provides an
interface for common database operations:

```python
class DatabaseManager:
    """Manages database operations."""

    def __init__(self, db_path=None):
        self.db_path = db_path or get_default_db_path()
        self.engine = create_engine(f"sqlite:///{self.db_path}")
        self.Session = sessionmaker(bind=self.engine)

    def create_tables(self):
        """Create all tables if they don't exist."""
        Base.metadata.create_all(self.engine)

    def get_session(self):
        """Get a new database session."""
        return self.Session()

    # Track operations
    def add_track(self, track_data):
        """Add a new track or update an existing one."""

    def get_track_by_spotify_id(self, spotify_id):
        """Get a track by its Spotify ID."""

    def get_tracks_by_criteria(self, criteria):
        """Get tracks matching the given criteria."""

    # Playlist operations
    def add_playlist(self, playlist_data):
        """Add a new playlist or update an existing one."""

    def get_playlist_by_spotify_id(self, spotify_id):
        """Get a playlist by its Spotify ID."""

    def add_track_to_playlist(self, playlist_id, track_id, position=None):
        """Add a track to a playlist."""

    # Listening history operations
    def add_listening_event(self, track_id, played_at, source="lastfm"):
        """Add a new listening event."""

    def get_recently_played_tracks(self, limit=10):
        """Get the most recently played tracks."""
```

## Query Examples

### Get Recently Added Tracks

```python
def get_recently_added_tracks(session, limit=10):
    return session.query(Track).order_by(Track.added_at.desc()).limit(limit).all()
```

### Get Recently Played Tracks

```python
def get_recently_played_tracks(session, limit=10):
    return session.query(Track).join(ListeningHistory).order_by(ListeningHistory.played_at.desc()).limit(limit).all()
```

### Get Most Played Tracks

```python
def get_most_played_tracks(session, limit=10):
    return session.query(Track).order_by(Track.play_count.desc()).limit(limit).all()
```

### Get Tracks Added in the Last N Days

```python
def get_tracks_added_in_last_days(session, days=7, limit=None):
    cutoff_date = datetime.utcnow() - timedelta(days=days)
    query = session.query(Track).filter(Track.added_at >= cutoff_date).order_by(Track.added_at.desc())
    if limit:
        query = query.limit(limit)
    return query.all()
```

### Get Tracks Played in the Last N Days

```python
def get_tracks_played_in_last_days(session, days=7, limit=None):
    cutoff_date = datetime.utcnow() - timedelta(days=days)
    query = session.query(Track).join(ListeningHistory).filter(ListeningHistory.played_at >= cutoff_date).order_by(ListeningHistory.played_at.desc())
    if limit:
        query = query.limit(limit)
    return query.all()
```

## Database Migrations

The application uses Alembic for database migrations. Migration scripts are
stored in the `migrations/` directory.

To create a new migration:

```bash
alembic revision --autogenerate -m "Description of changes"
```

To apply migrations:

```bash
alembic upgrade head
```

## Performance Considerations

### Indexes

Indexes are created on frequently queried columns to improve performance:
- Primary keys are automatically indexed
- Foreign keys are indexed for join operations
- Timestamp fields used for filtering (added_at, played_at) are indexed
- Fields used for lookups (spotify_id, name) are indexed

### Query Optimization

For optimal performance:
- Use specific queries instead of loading all records
- Use joins instead of separate queries when possible
- Use pagination for large result sets
- Consider using eager loading for relationships when appropriate

### Database Maintenance

Regular maintenance tasks:
- Periodic VACUUM to reclaim space and optimize the database
- Regular backups to prevent data loss
- Consider using WAL (Write-Ahead Logging) mode for better concurrency

## Troubleshooting

### Common Issues

1. **Database Locked**
   - Ensure only one process is writing to the database at a time
   - Check for long-running transactions
   - Consider using a timeout for database connections

2. **Slow Queries**
   - Check that appropriate indexes are in place
   - Review query execution plans
   - Consider denormalizing data for frequently accessed information

3. **Data Inconsistencies**
   - Use transactions for related operations
   - Implement constraints to enforce data integrity
   - Add validation at the application level

### Debugging

To enable SQLAlchemy query logging:

```python
import logging
logging.basicConfig()
logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)
```

This will log all SQL queries to the console, which can be helpful for
debugging.

