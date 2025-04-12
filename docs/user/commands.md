# Command Reference

This document provides detailed information about all available commands in the mkplaylist application.

## Global Options

These options can be used with any command:

| Option | Description |
|--------|-------------|
| `--help`, `-h` | Show help message and exit |
| `--version`, `-v` | Show version information and exit |
| `--config FILE`, `-c FILE` | Specify a custom configuration file |
| `--verbose` | Enable verbose output for debugging |

## Commands

### `sync`

Synchronizes data from Spotify and Last.fm to the local database.

```bash
mkplaylist sync [OPTIONS]
```

#### Options

| Option | Description |
|--------|-------------|
| `--spotify-only` | Only sync data from Spotify |
| `--lastfm-only` | Only sync data from Last.fm |
| `--full` | Perform a full sync instead of incremental |
| `--days DAYS` | Number of days of history to sync (default: 30) |

#### Examples

```bash
# Perform a standard incremental sync
mkplaylist sync

# Sync only Spotify data
mkplaylist sync --spotify-only

# Perform a full sync of all data
mkplaylist sync --full

# Sync the last 7 days of listening history
mkplaylist sync --days 7
```

### `create`

Creates or updates a Spotify playlist based on custom criteria.

```bash
mkplaylist create PLAYLIST_NAME CRITERIA [OPTIONS]
```

#### Arguments

| Argument | Description |
|----------|-------------|
| `PLAYLIST_NAME` | Name for the playlist (will be created if it doesn't exist) |
| `CRITERIA` | Custom criteria string for selecting tracks |

#### Options

| Option | Description |
|--------|-------------|
| `--description TEXT` | Custom description for the playlist |
| `--public` | Make the playlist public (default: private) |
| `--collaborative` | Make the playlist collaborative |
| `--replace` | Replace all tracks in the playlist (default: append) |
| `--limit N` | Maximum number of tracks to include |

#### Examples

```bash
# Create a playlist with recently added and played tracks
mkplaylist create "Recent Favorites" "10 most recently added songs and 10 last played songs"

# Create a public playlist with a custom description
mkplaylist create "Weekly Discoveries" "20 most recently added songs" --public --description "My weekly discoveries"

# Replace all tracks in an existing playlist
mkplaylist create "Daily Mix" "5 last played songs" --replace

# Limit the number of tracks
mkplaylist create "Top Tracks" "most played songs" --limit 50
```

### `list`

Lists all playlists that have been created or updated by mkplaylist.

```bash
mkplaylist list [OPTIONS]
```

#### Options

| Option | Description |
|--------|-------------|
| `--format {table,json,csv}` | Output format (default: table) |
| `--sort {name,date,updated}` | Sort order (default: updated) |

#### Examples

```bash
# List all playlists in table format
mkplaylist list

# List playlists in JSON format
mkplaylist list --format json

# List playlists sorted by name
mkplaylist list --sort name
```

### `info`

Shows detailed information about a specific playlist.

```bash
mkplaylist info PLAYLIST_NAME [OPTIONS]
```

#### Arguments

| Argument | Description |
|----------|-------------|
| `PLAYLIST_NAME` | Name of the playlist to show information for |

#### Options

| Option | Description |
|--------|-------------|
| `--format {table,json,csv}` | Output format (default: table) |
| `--show-tracks` | Include track listing in the output |

#### Examples

```bash
# Show information about a playlist
mkplaylist info "Recent Favorites"

# Show information including tracks in JSON format
mkplaylist info "Recent Favorites" --show-tracks --format json
```

### `delete`

Deletes a playlist from Spotify.

```bash
mkplaylist delete PLAYLIST_NAME [OPTIONS]
```

#### Arguments

| Argument | Description |
|----------|-------------|
| `PLAYLIST_NAME` | Name of the playlist to delete |

#### Options

| Option | Description |
|--------|-------------|
| `--force` | Skip confirmation prompt |
| `--local-only` | Only remove from local database, not from Spotify |

#### Examples

```bash
# Delete a playlist (with confirmation)
mkplaylist delete "Old Playlist"

# Force delete without confirmation
mkplaylist delete "Temporary Playlist" --force

# Only remove from local database
mkplaylist delete "Test Playlist" --local-only
```

## Criteria Syntax

The `create` command uses a custom criteria syntax to specify which tracks to include in a playlist. Here are the supported patterns:

| Pattern | Description | Example |
|---------|-------------|---------|
| `X most recently added songs` | The X most recently added tracks | `10 most recently added songs` |
| `X last played songs` | The X most recently played tracks | `5 last played songs` |
| `X most played songs` | The X most frequently played tracks | `20 most played songs` |
| `songs by ARTIST` | Tracks by a specific artist | `songs by The Beatles` |
| `songs from ALBUM` | Tracks from a specific album | `songs from Abbey Road` |
| `songs in GENRE` | Tracks in a specific genre | `songs in rock` |
| `songs added in the last X days` | Tracks added within the specified time period | `songs added in the last 7 days` |
| `songs played in the last X days` | Tracks played within the specified time period | `songs played in the last 30 days` |

These patterns can be combined using `and` to create more complex criteria:

```
10 most recently added songs and 5 last played songs
```

```
songs by The Beatles and songs from Abbey Road
```

```
5 most played songs and songs played in the last 7 days
```

For more examples, see the [Examples](examples.md) document.
