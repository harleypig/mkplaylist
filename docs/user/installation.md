
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

### Using pipx (Recommended)

The recommended way to install mkplaylist is using [pipx](https://pypa.github.io/pipx/), which installs the package in an isolated environment while making the command available in your PATH:

```bash
# Install pipx if you don't have it
python -m pip install --user pipx
python -m pipx ensurepath

# Install mkplaylist directly from the GitHub repository
pipx install git+https://github.com/harleypig/mkplaylist.git
```

Using pipx provides several benefits:
- Isolates dependencies to avoid conflicts with other packages
- Makes the command available globally without affecting your system Python
- Simplifies updates and uninstallation
- Manages virtual environments automatically

### Using pip

If you prefer, you can also install mkplaylist using pip directly from the GitHub repository:

```bash
pip install git+https://github.com/harleypig/mkplaylist.git
```

If you prefer, you can also install mkplaylist using pip:

```bash
pip install mkplaylist
```

### Installing from Source

For development or if you want to make modifications:

If you prefer to install from source:

1. Clone the repository:
   ```bash
   
   ```bash
   git clone https://github.com/harleypig/mkplaylist.git
   cd mkplaylist
   ```
   
2. Install the package in development mode:
   ```bash
   
   ```bash
   pip install -e .
   ```

This method is useful if you plan to modify the code or contribute to the project.

## Configuration

After installation, you'll need to configure mkplaylist with your API
credentials:

1. Create a `.env` file in your working directory (or copy the provided `.env.example`):
   ```
   ```
   SPOTIFY_CLIENT_ID=your_spotify_client_id
   SPOTIFY_CLIENT_SECRET=your_spotify_client_secret
   SPOTIFY_REDIRECT_URI=http://localhost:8888/callback
   LASTFM_API_KEY=your_lastfm_api_key
   LASTFM_API_SECRET=your_lastfm_shared_secret
   ```

   ```

2. Replace the placeholder values with your actual API credentials

### Configuration Precedence

mkplaylist supports two methods for configuration:

1. **Environment Variables**: You can set configuration values directly as environment variables
2. **`.env` File**: You can create a `.env` file in your working directory

The configuration system follows this precedence order:

1. Environment variables are loaded first as baseline configuration
2. Values from `.env` file override environment variables if present

This approach gives you flexibility in how you configure the application:

#### Using Environment Variables Only

You can set environment variables directly in your shell:

```bash
export SPOTIFY_CLIENT_ID=your_spotify_client_id
export SPOTIFY_CLIENT_SECRET=your_spotify_client_secret
export SPOTIFY_REDIRECT_URI=http://localhost:8888/callback
export LASTFM_API_KEY=your_lastfm_api_key
export LASTFM_API_SECRET=your_lastfm_shared_secret
mkplaylist --version
```

#### Using .env File Only

Create a `.env` file in your working directory with your configuration:

```
SPOTIFY_CLIENT_ID=your_spotify_client_id
SPOTIFY_CLIENT_SECRET=your_spotify_client_secret
SPOTIFY_REDIRECT_URI=http://localhost:8888/callback
LASTFM_API_KEY=your_lastfm_api_key
LASTFM_API_SECRET=your_lastfm_shared_secret
```

Then run mkplaylist normally:

```bash
mkplaylist --version
```

#### Using Both Methods

You can set some values as environment variables and others in the `.env` file. If the same value is set in both places, the `.env` file value takes precedence.

For example, with these environment variables:

```bash
export SPOTIFY_CLIENT_ID=env_spotify_client_id
export SPOTIFY_CLIENT_SECRET=env_spotify_client_secret
```

And this `.env` file:

```
SPOTIFY_CLIENT_ID=dotenv_spotify_client_id
LASTFM_API_KEY=dotenv_lastfm_api_key
```

The resulting configuration would be:
- `SPOTIFY_CLIENT_ID`: `dotenv_spotify_client_id` (from `.env` file)
- `SPOTIFY_CLIENT_SECRET`: `env_spotify_client_secret` (from environment)
- `LASTFM_API_KEY`: `dotenv_lastfm_api_key` (from `.env` file)

This flexibility allows you to:
- Use environment variables for CI/CD pipelines
- Use `.env` file for local development
- Override specific values as needed

## Verifying Installation

To verify that mkplaylist is installed correctly, run:

```bash
```bash
mkplaylist --version
```

If you installed with pipx, you can also verify the installation with:

```bash
```bash
pipx list
```

For repository installations, you can check which version you have installed:

```bash
pip show mkplaylist
```

This will display information about the installed package, including the version and where it was installed from.

This will show all applications installed with pipx, including mkplaylist.

## Next Steps

Once you've successfully installed mkplaylist, proceed to the [Getting Started
Guide](getting_started.md) to learn how to use the application.

## Troubleshooting

### Common Issues

1. **"Command not found" error**
   - If installed with pipx: Run `pipx ensurepath` and restart your terminal
   - If installed with pip: Ensure that Python's bin directory is in your PATH
   - Try using `python -m mkplaylist` instead

2. **Authentication errors**
   - Double-check your API credentials in the `.env` file
   - Ensure your Spotify redirect URI matches what you registered

3. **Package dependencies issues**
   - If installed with pipx: Try reinstalling with `pipx uninstall mkplaylist && pipx install git+https://github.com/harleypig/mkplaylist.git`
   - If installed with pip: Try reinstalling with `pip install --upgrade --force-reinstall git+https://github.com/harleypig/mkplaylist.git`

4. **pipx installation issues**
   - Make sure you have Python 3.7+ installed
   - Try running `python -m pip install --user --upgrade pipx`
   - On some systems, you may need to log out and log back in after running `pipx ensurepath`

5. **Git repository access issues**
   - Ensure you have Git installed on your system
   - Check your internet connection
   - If behind a firewall, ensure you have access to GitHub

If you encounter any other issues, please check the project's GitHub repository for known issues or to report a new one.
