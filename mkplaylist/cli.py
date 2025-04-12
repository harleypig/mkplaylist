
"""
Command-line interface for mkplaylist.

This module provides the CLI commands for interacting with the application.
"""

import sys
import logging
from typing import Optional, List

import click

from mkplaylist import __version__
from mkplaylist.config import MkPlaylistConfig

from mkplaylist import config

# Set up logging
config = MkPlaylistConfig()
logging.basicConfig(
  level=getattr(logging, config.LOG_LEVEL),
  format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@click.group()
@click.version_option(version=__version__)
def cli():
  """
    Create Spotify playlists based on custom criteria using Last.fm data.
    
    This tool allows you to sync data from Spotify and Last.fm, and then
    create playlists based on criteria like "recently added" and "last played".
    """
  # Check configuration
  issues = config.validate_config()
  if issues:
    click.echo("Configuration issues detected:")
    for key, message in issues.items():
      click.echo(f"  - {message}")
    click.echo(
      "\nPlease set the required environment variables or create a .env file."
    )
    click.echo("See the documentation for more information.")
    sys.exit(1)


@cli.command()
@click.option(
  '--spotify-only', is_flag=True, help='Only sync data from Spotify'
)
@click.option(
  '--lastfm-only', is_flag=True, help='Only sync data from Last.fm'
)
@click.option(
  '--full', is_flag=True, help='Perform a full sync instead of incremental'
)
@click.option(
  '--days',
  type=int,
  default=config.DEFAULT_SYNC_DAYS,
  help=f'Number of days of history to sync (default: {config.DEFAULT_SYNC_DAYS})'
)
def sync(spotify_only: bool, lastfm_only: bool, full: bool, days: int):

  """
    Synchronize data from Spotify and Last.fm to the local database.
    """
  click.echo("Syncing data...")

  if spotify_only and lastfm_only:
    click.echo("Error: Cannot specify both --spotify-only and --lastfm-only")
    sys.exit(1)

  if spotify_only:
    click.echo("Syncing Spotify data only...")
    # TODO: Implement Spotify sync
  elif lastfm_only:
    click.echo("Syncing Last.fm data only...")
    # TODO: Implement Last.fm sync
  else:
    click.echo("Syncing both Spotify and Last.fm data...")
    # TODO: Implement full sync

  if full:
    click.echo("Performing full sync...")
  else:
    click.echo(f"Syncing last {days} days of history...")

  click.echo("Sync completed successfully!")


@cli.command()
@click.argument('playlist_name')
@click.argument('criteria')
@click.option('--description', help='Custom description for the playlist')
@click.option(
  '--public', is_flag=True, help='Make the playlist public (default: private)'
)
@click.option(
  '--collaborative', is_flag=True, help='Make the playlist collaborative'
)
@click.option(
  '--replace',
  is_flag=True,
  help='Replace all tracks in the playlist (default: append)'
)
@click.option('--limit', type=int, help='Maximum number of tracks to include')
def create(
  playlist_name: str, criteria: str, description: Optional[str], public: bool,
  collaborative: bool, replace: bool, limit: Optional[int]
):
  """
    Create or update a Spotify playlist based on custom criteria.
    
    PLAYLIST_NAME is the name for the playlist (will be created if it doesn't exist).
    
    CRITERIA is a custom criteria string for selecting tracks, such as:
    "10 most recently added songs and 10 last played songs"
    """
  click.echo(f"Creating playlist: {playlist_name}")
  click.echo(f"Criteria: {criteria}")

  # Additional options
  if description:
    click.echo(f"Description: {description}")
  click.echo(f"Public: {public}")
  click.echo(f"Collaborative: {collaborative}")
  click.echo(f"Replace existing tracks: {replace}")
  if limit:
    click.echo(f"Track limit: {limit}")

  # TODO: Implement playlist creation
  click.echo("Parsing criteria...")
  click.echo("Querying database...")
  click.echo("Creating playlist...")
  click.echo("Playlist created successfully!")


@cli.command()
@click.option(
  '--format',
  type=click.Choice(['table', 'json', 'csv']),
  default='table',
  help='Output format (default: table)'
)
@click.option(
  '--sort',
  type=click.Choice(['name', 'date', 'updated']),
  default='updated',
  help='Sort order (default: updated)'
)
def list(format: str, sort: str):
  """
    List all playlists that have been created or updated by mkplaylist.
    """
  click.echo("Listing playlists...")
  click.echo(f"Format: {format}")
  click.echo(f"Sort: {sort}")

  # TODO: Implement playlist listing
  click.echo(
    "No playlists found. Use 'mkplaylist create' to create a playlist."
  )


def main():
  """Main entry point for the CLI."""
  try:
    cli()
  except Exception as e:
    logger.error(f"An error occurred: {e}", exc_info=True)
    click.echo(f"Error: {e}")
    sys.exit(1)


if __name__ == '__main__':
  main()
