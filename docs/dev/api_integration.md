# API Integration

This document provides detailed information about the integration with external APIs in the mkplaylist application.

## Overview

mkplaylist integrates with two primary external APIs:

1. **Spotify API** - For accessing and managing playlists, tracks, and user data
2. **Last.fm API** - For retrieving listening history and track metadata

These integrations are handled by dedicated client classes in the `mkplaylist/api/` directory.

## Spotify API Integration

### Authentication

Spotify uses OAuth 2.0 for authentication. The application implements the Authorization Code flow:

1. User is redirected to Spotify's authorization page
2. User grants permissions to the application
3. Spotify redirects back with an authorization code
4. Application exchanges the code for access and refresh tokens
5. Access token is used for API requests
6. Refresh token is used to obtain new access tokens when they expire

### Required Permissions (Scopes)

The application requires the following Spotify scopes:

- `user-read-private` - Read access to user's subscription details
- `user-read-email` - Read access to user's email
- `playlist-read-private` - Read access to user's private playlists
- `playlist-read-collaborative` - Read access to user's collaborative playlists
- `playlist-modify-public` - Write access to user's public playlists
- `playlist-modify-private` - Write access to user's private playlists
- `user-library-read` - Read access to user's saved tracks and albums

### Key Endpoints

| Endpoint | Purpose | Implementation |
|----------|---------|----------------|
| `GET /v1/me` | Get current user profile | `get_current_user()` |
| `GET /v1/me/playlists` | Get user's playlists | `get_user_playlists()` |
| `GET /v1/playlists/{id}` | Get a specific playlist | `get_playlist(playlist_id)` |
| `GET /v1/playlists/{id}/tracks` | Get tracks in a playlist | `get_playlist_tracks(playlist_id)` |
| `POST /v1/users/{user_id}/playlists` | Create a new playlist | `create_playlist(name, description, public)` |
| `POST /v1/playlists/{id}/tracks` | Add tracks to a playlist | `add_tracks_to_playlist(playlist_id, track_uris)` |
| `PUT /v1/playlists/{id}/tracks` | Replace tracks in a playlist | `replace_playlist_tracks(playlist_id, track_uris)` |
| `DELETE /v1/playlists/{id}/tracks` | Remove tracks from a playlist | `remove_tracks_from_playlist(playlist_id, track_uris)` |

### Rate Limiting

Spotify API has rate limits that must be respected:

- Short-term rate limit: 1000 requests per 25 seconds
- Long-term rate limit: 10,000 requests per day

The application implements exponential backoff for retrying requests when rate limits are encountered.

### Error Handling

Common Spotify API errors and their handling:

| Status Code | Error | Handling Strategy |
|-------------|-------|-------------------|
| 401 | Unauthorized | Refresh access token and retry |
| 403 | Forbidden | Check scopes and notify user |
| 429 | Too Many Requests | Wait for the duration specified in Retry-After header |
| 500, 502, 503 | Server Errors | Exponential backoff and retry |

## Last.fm API Integration

### Authentication

Last.fm API uses a simpler authentication model:

1. API Key - Required for all requests
2. API Secret - Used for signing requests that require authentication
3. Session Key - Optional, used for authenticated requests

### Key Endpoints

| Endpoint | Purpose | Implementation |
|----------|---------|----------------|
| `user.getRecentTracks` | Get user's recently played tracks | `get_recent_tracks(username, limit, from_date, to_date)` |
| `user.getTopTracks` | Get user's most played tracks | `get_top_tracks(username, period, limit)` |
| `track.getInfo` | Get detailed track information | `get_track_info(artist, track, username)` |
| `track.scrobble` | Scrobble a track (mark as played) | `scrobble_track(artist, track, timestamp)` |

### Rate Limiting

Last.fm API has the following rate limits:

- 5 requests per second
- 1000 requests per day for unauthenticated calls
- 5000 requests per day for authenticated calls

The application implements a request throttling mechanism to stay within these limits.

### Error Handling

Common Last.fm API errors and their handling:

| Error Code | Error | Handling Strategy |
|------------|-------|-------------------|
| 6 | Invalid parameters | Log error and notify user |
| 8 | Operation failed | Retry with exponential backoff |
| 9 | Invalid session key | Re-authenticate and retry |
| 11, 16 | Service offline/temporarily unavailable | Retry with exponential backoff |
| 29 | Rate limit exceeded | Wait and retry with longer intervals |

## Implementation Details

### Spotify Client

The `SpotifyClient` class in `spotify_client.py` handles all Spotify API interactions:

```python
class SpotifyClient:
    def __init__(self, client_id, client_secret, redirect_uri):
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri
        self.sp = None  # Spotipy client instance
        
    def authenticate(self):
        # Handle authentication flow
        
    def get_user_playlists(self):
        # Fetch and return user's playlists
        
    def create_playlist(self, name, description="", public=False):
        # Create a new playlist
        
    # Additional methods for playlist and track operations
```

### Last.fm Client

The `LastFmClient` class in `lastfm_client.py` handles all Last.fm API interactions:

```python
class LastFmClient:
    def __init__(self, api_key, api_secret, username=None):
        self.api_key = api_key
        self.api_secret = api_secret
        self.username = username
        self.network = None  # pylast network instance
        
    def authenticate(self):
        # Set up authentication
        
    def get_recent_tracks(self, limit=50, from_date=None, to_date=None):
        # Fetch and return recently played tracks
        
    def get_top_tracks(self, period="overall", limit=50):
        # Fetch and return most played tracks
        
    # Additional methods for track operations
```

## Data Mapping

### Spotify to Database Mapping

| Spotify Object | Database Model | Notes |
|----------------|----------------|-------|
| Track | `Track` | Includes URI, name, artists, album |
| Playlist | `Playlist` | Includes Spotify ID, name, description |
| Playlist Track | `PlaylistTrack` | Junction table with added_at timestamp |

### Last.fm to Database Mapping

| Last.fm Object | Database Model | Notes |
|----------------|----------------|-------|
| Recent Track | `ListeningHistory` | Includes track reference and played_at timestamp |
| Track Info | Updates to `Track` | Additional metadata like tags |

## Matching Strategy

A key challenge is matching tracks between Spotify and Last.fm. The application uses the following strategy:

1. **Exact Match**: Artist name and track title match exactly
2. **Normalized Match**: Comparison after normalizing strings (removing special characters, etc.)
3. **Fuzzy Match**: For cases with slight differences, using Levenshtein distance
4. **Manual Resolution**: For ambiguous cases, store potential matches for later resolution

## Testing API Integrations

For testing API integrations without making actual API calls:

1. **Mock Responses**: Sample responses are stored in `tests/fixtures/`
2. **VCR Cassettes**: Using the `vcrpy` library to record and replay API interactions
3. **API Simulators**: Mock servers that simulate API behavior for testing

See the [Contributing Guide](contributing.md) for more information on testing API integrations.

## Adding New API Integrations

To add support for a new music service:

1. Create a new client class in `mkplaylist/api/`
2. Implement the required authentication flow
3. Add methods for fetching playlists and tracks
4. Update the database models if necessary
5. Extend the sync service to use the new client
6. Add appropriate tests

## Troubleshooting

Common API integration issues and solutions:

1. **Authentication Failures**
   - Check that API credentials are correct
   - Verify that redirect URI matches exactly what's registered
   - Ensure required scopes are requested

2. **Rate Limiting**
   - Implement proper request throttling
   - Add exponential backoff for retries
   - Consider caching frequently accessed data

3. **Data Inconsistencies**
   - Improve matching algorithm
   - Log unmatched tracks for review
   - Consider additional metadata sources for resolution

4. **API Changes**
   - Monitor API changelogs
   - Design client classes to be adaptable
   - Version your database schema to handle changes
