# Examples

This document provides practical examples of using mkplaylist to create dynamic Spotify playlists based on various criteria.

## Basic Examples

### Recently Added Tracks

Create a playlist of your most recently added tracks:

```bash
mkplaylist create "Recently Added" "20 most recently added songs"
```

### Recently Played Tracks

Create a playlist of your most recently played tracks:

```bash
mkplaylist create "Recently Played" "15 last played songs"
```

### Most Played Tracks

Create a playlist of your most frequently played tracks:

```bash
mkplaylist create "Most Played" "25 most played songs"
```

## Combined Criteria Examples

### Recent Favorites

Create a playlist combining recently added and recently played tracks:

```bash
mkplaylist create "Recent Favorites" "10 most recently added songs and 10 last played songs"
```

### Weekly Rotation

Create a playlist of tracks added in the last week and played in the last week:

```bash
mkplaylist create "Weekly Rotation" "songs added in the last 7 days and songs played in the last 7 days"
```

### Artist Focus

Create a playlist of recently played tracks by a specific artist:

```bash
mkplaylist create "Recent Beatles" "songs by The Beatles and 20 last played songs"
```

## Advanced Examples

### Daily Mix

Create a daily mix playlist that replaces all tracks each day:

```bash
mkplaylist create "Daily Mix" "5 most recently added songs and 10 last played songs" --replace
```

### Collaborative Playlist

Create a collaborative playlist that friends can add to:

```bash
mkplaylist create "Friend Mix" "20 most played songs" --collaborative --description "Our favorite tracks"
```

### Limited Selection

Create a playlist with a maximum number of tracks:

```bash
mkplaylist create "Top 50" "most played songs" --limit 50
```

## Workflow Examples

### Weekly Discovery Playlist

This example shows how to maintain a weekly discovery playlist:

1. Sync your data:
   ```bash
   mkplaylist sync
   ```

2. Create a playlist of tracks added in the last week:
   ```bash
   mkplaylist create "Weekly Discoveries" "songs added in the last 7 days" --replace --description "New tracks from the past week"
   ```

3. Schedule this to run weekly (using cron or similar):
   ```bash
   0 0 * * 0 mkplaylist sync && mkplaylist create "Weekly Discoveries" "songs added in the last 7 days" --replace
   ```

### Monthly Retrospective

Create a monthly playlist of your most played tracks:

1. At the end of each month, sync your data:
   ```bash
   mkplaylist sync --days 30
   ```

2. Create a playlist of your most played tracks from the month:
   ```bash
   mkplaylist create "April 2023 Favorites" "songs played in the last 30 days" --description "My most played tracks in April 2023"
   ```

### Genre Exploration

Create playlists to explore specific genres:

```bash
mkplaylist create "Jazz Exploration" "songs in jazz and songs played in the last 90 days"
```

```bash
mkplaylist create "Recent Rock" "songs in rock and 30 most recently added songs"
```

## Combining Multiple Criteria

You can combine multiple criteria to create highly specific playlists:

```bash
mkplaylist create "Recent Indie Favorites" "songs in indie and 10 most recently added songs and 10 last played songs"
```

```bash
mkplaylist create "Throwback Mix" "songs added more than 365 days ago and 20 most played songs"
```

## Maintenance Examples

### Updating an Existing Playlist

To update an existing playlist with new tracks matching the same criteria:

```bash
# First, sync to get the latest data
mkplaylist sync

# Then run the same create command (tracks will be appended by default)
mkplaylist create "Recent Favorites" "10 most recently added songs and 10 last played songs"
```

### Replacing All Tracks

To completely replace all tracks in an existing playlist:

```bash
mkplaylist create "Daily Mix" "5 most recently added songs and 10 last played songs" --replace
```

### Deleting a Playlist

To delete a playlist when you no longer need it:

```bash
mkplaylist delete "Temporary Playlist"
```

## Tips for Creating Effective Playlists

1. **Be specific with criteria** - More specific criteria generally yield better results
2. **Combine different types of criteria** - Mix recency, frequency, and metadata criteria
3. **Use the `--limit` option** - Control the size of your playlists
4. **Add descriptions** - Use the `--description` option to document the purpose of the playlist
5. **Update regularly** - Keep your playlists fresh by updating them periodically

Remember that the effectiveness of your criteria depends on the quality and quantity of your listening data. Regular syncing ensures that your playlists reflect your current listening habits.
