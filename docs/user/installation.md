# Installation Guide

This guide will walk you through the process of installing the mkplaylist
application.

## Prerequisites

Before installing mkplaylist, ensure you have the following:

1. **Python 3.7+** - The application requires Python 3.7 or newer
2. **Spotify Account** - You'll need a Spotify account to access playlists
3. **Last.fm Account** - You'll need a Last.fm account to access listening history
4. **API Credentials** - You'll need to register for API access with both services

### Obtaining API Credentials

#### Spotify API Credentials

1. Visit the [Spotify Developer Dashboard](https://developer.spotify.com/dashboard/)
2. Log in with your Spotify account
3. Click "Create an App"
4. Fill in the application name (e.g., "mkplaylist") and description
5. Accept the terms and conditions
6. Once created, you'll see your Client ID and Client Secret
7. Add a redirect URI (e.g., `http://localhost:8888/callback`)

#### Last.fm API Credentials

1. Visit the [Last.fm API page](https://www.last.fm/api/account/create)
2. Log in with your Last.fm account
3. Fill in the application name and other required details
4. Once submitted, you'll receive an API Key and Shared Secret

## Installation Methods

### Using pip (Recommended)

The simplest way to install mkplaylist is using pip:

```bash
pip install mkplaylist
```

### Installing from Source

If you prefer to install from source:

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/mkplaylist.git
   cd mkplaylist
   ```

2. Install the package in development mode:
   ```bash
   pip install -e .
   ```

## Configuration

After installation, you'll need to configure mkplaylist with your API
credentials:

1. Create a `.env` file in your working directory (or copy the provided `.env.example`):
   ```
   SPOTIFY_CLIENT_ID=your_spotify_client_id
   SPOTIFY_CLIENT_SECRET=your_spotify_client_secret
   SPOTIFY_REDIRECT_URI=http://localhost:8888/callback
   LASTFM_API_KEY=your_lastfm_api_key
   LASTFM_API_SECRET=your_lastfm_shared_secret
   ```

2. Replace the placeholder values with your actual API credentials

## Verifying Installation

To verify that mkplaylist is installed correctly, run:

```bash
mkplaylist --version
```

You should see the version number of the installed package.

## Next Steps

Once you've successfully installed mkplaylist, proceed to the [Getting Started
Guide](getting_started.md) to learn how to use the application.

## Troubleshooting

### Common Issues

1. **"Command not found" error**
   - Ensure that Python's bin directory is in your PATH
   - Try using `python -m mkplaylist` instead

2. **Authentication errors**
   - Double-check your API credentials in the `.env` file
   - Ensure your Spotify redirect URI matches what you registered

3. **Package dependencies issues**
   - Try reinstalling with `pip install --upgrade --force-reinstall mkplaylist`

If you encounter any other issues, please check the project's GitHub
repository for known issues or to report a new one.
