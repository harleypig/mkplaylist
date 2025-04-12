# Architecture Overview

This document provides a detailed overview of the mkplaylist application
architecture, explaining how the different components interact and the design
decisions behind them.

## High-Level Architecture

mkplaylist follows a layered architecture with clear separation of concerns:

```
┌─────────────────┐
│  CLI Interface  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐     ┌─────────────────┐
│    Services     │◄───►│  API Clients    │
└────────┬────────┘     └─────────────────┘
         │                      ▲
         ▼                      │
┌─────────────────┐             │
│  Database Layer │             │
└────────┬────────┘             │
         │                      │
         ▼                      │
┌─────────────────┐     ┌───────┴───────┐
│  SQLite Database│     │ External APIs │
└─────────────────┘     └───────────────┘
```

### Key Components

1. **CLI Interface** (`mkplaylist/cli.py`)
   - Handles user input and command parsing
   - Provides feedback to the user
   - Delegates actual work to the service layer

2. **Services** (`mkplaylist/services/`)
   - `sync_service.py`: Manages synchronization of data from external APIs to local database
   - `playlist_service.py`: Handles playlist creation and management
   - `query_parser.py`: Parses natural language-like criteria into database queries

3. **API Clients** (`mkplaylist/api/`)
   - `spotify_client.py`: Handles communication with Spotify API
   - `lastfm_client.py`: Handles communication with Last.fm API
   - Manages authentication, rate limiting, and error handling

4. **Database Layer** (`mkplaylist/database/`)
   - `models.py`: Defines SQLAlchemy models representing database tables
   - `db_manager.py`: Provides an interface for database operations

5. **Configuration** (`mkplaylist/config.py`)
   - Manages application configuration
   - Handles environment variables and secrets

## Data Flow

### Synchronization Flow

1. User initiates sync via CLI
2. `sync_service.py` coordinates the process
3. API clients fetch data from Spotify and Last.fm
4. Data is normalized and processed
5. Database is updated with new information

```
User → CLI → SyncService → API Clients → External APIs
                 ↓
               Data Processing
                 ↓
               Database
```

### Playlist Creation Flow

1. User provides criteria via CLI
2. `query_parser.py` parses the criteria
3. `playlist_service.py` queries the database
4. Results are processed and filtered
5. New playlist is created via Spotify API

```
User → CLI → QueryParser → PlaylistService → Database
                                ↓
                              Results Processing
                                ↓
                              SpotifyClient → Spotify API
```

## Design Decisions

### SQLite Database

We chose SQLite for several reasons:
- No need for a separate database server
- Simple setup and maintenance
- Sufficient performance for the expected data volume
- Easy portability and backup

### SQLAlchemy ORM

Using SQLAlchemy provides:
- Database-agnostic code (potential to switch to other databases)
- Object-oriented interface to the database
- Simplified query construction
- Automatic schema management

### Separation of API Clients

By isolating API clients:
- We can handle API-specific authentication and rate limiting
- Changes to APIs require updates only to the relevant client
- We can mock API responses for testing
- We can potentially add support for other music services

### Natural Language Query Parser

The custom query parser allows:
- Intuitive user experience with natural language-like commands
- Flexibility to support various criteria combinations
- Extensibility to add new criteria types

## Error Handling Strategy

The application implements a layered error handling approach:

1. **API-level errors**: Handled by API clients, with retries for transient issues
2. **Service-level errors**: Handled by services, with appropriate fallbacks
3. **CLI-level errors**: Presented to the user with helpful messages

## Authentication Flow

### Spotify Authentication

1. First-time use triggers OAuth flow
2. User is directed to Spotify login page
3. After authorization, tokens are stored locally
4. Refresh tokens are used for subsequent access

### Last.fm Authentication

1. API key is used for authentication
2. User session is established if needed for certain operations

## Performance Considerations

- Incremental syncs to minimize API calls
- Efficient database queries using indexes
- Caching of frequently accessed data
- Batch processing for large datasets

## Future Architecture Extensions

The architecture is designed to be extensible in several ways:

1. **Additional Music Services**
   - New API clients can be added for other streaming services
   - Database models can be extended to store service-specific data

2. **Advanced Query Capabilities**
   - The query parser can be enhanced to support more complex criteria
   - Machine learning could be integrated for smart playlist generation

3. **Web Interface**
   - A web server component could be added
   - The service layer would remain unchanged, with a new presentation layer

4. **Distributed Architecture**
   - For larger deployments, components could be separated
   - Database could be migrated to a dedicated server

## Development Considerations

For information on how to extend or modify the architecture, see the
[Contributing Guide](contributing.md).
