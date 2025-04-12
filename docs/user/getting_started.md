# Getting Started with mkplaylist

This guide will help you get started with using mkplaylist to create dynamic
Spotify playlists based on your listening history from Last.fm.

## Initial Setup

Before you can start creating playlists, you need to:

1. Complete the [installation process](installation.md)
2. Authenticate with Spotify and Last.fm
3. Perform an initial data sync

## Authentication

The first time you run a mkplaylist command, you'll be prompted to
authenticate with both Spotify and Last.fm:

```bash
mkplaylist sync
```

This will:

1. Open a browser window for Spotify authentication
2. Ask you to authorize the application
3. Redirect you back to the application
4. Store the authentication tokens for future use

## Data Synchronization

Before creating playlists, you need to sync your data from Spotify and
Last.fm:

```bash
mkplaylist sync
```

This command:

1. Fetches your existing Spotify playlists
2. Retrieves your listening history from Last.fm
3. Stores this data in a local SQLite database
4. Matches tracks between the two services

The initial sync may take some time depending on how many playlists you have
and how extensive your listening history is. Subsequent syncs will be faster
as they only fetch new data.

## Creating Your First Playlist

Once your data is synced, you can create a playlist using custom criteria:

```bash
mkplaylist create "recent-favorites" "10 most recently added songs and 10 last played songs"
```

This command:

1. Parses your criteria ("10 most recently added songs and 10 last played songs")
2. Queries your local database for tracks matching these criteria
3. Creates a new Spotify playlist named "recent-favorites"
4. Adds the matching tracks to the playlist

## Understanding Criteria Syntax

The criteria string uses natural language-like syntax to specify which tracks
to include:

- **Recently added tracks**: `X most recently added songs`
- **Recently played tracks**: `X last played songs`
- **Combining criteria**: Use `and` to combine multiple criteria

For example:
- `"5 most recently added songs"`
- `"10 last played songs"`
- `"5 most recently added songs and 10 last played songs"`

See the [Examples](examples.md) document for more complex criteria examples.

## Listing Available Playlists

To see all playlists that have been created or updated by mkplaylist:

```bash
mkplaylist list
```

This will show:
- Playlist names
- When they were created/updated
- The criteria used to create them

## Regular Usage

For regular usage, we recommend:

1. Running `mkplaylist sync` periodically to keep your data up to date
2. Creating playlists with specific criteria as needed
3. Updating existing playlists by running the same create command again

## Next Steps

- Check out the [Command Reference](commands.md) for detailed information on all available commands
- See the [Examples](examples.md) document for more complex usage examples
- Explore different criteria combinations to create personalized playlists

## Tips for Best Results

- Sync your data regularly to ensure your playlists reflect your latest listening habits
- Be specific with your criteria to get the most relevant results
- Start with simple criteria and gradually experiment with more complex combinations
- Use meaningful playlist names that reflect the criteria used to create them
