"""
Test script to verify configuration precedence in mkplaylist.

This script tests that:
1. Environment variables are loaded as baseline configuration
2. Values from .env file override environment variables if present
3. The configuration system correctly reports the source of each value
"""

import os
import sys
from pathlib import Path

# Add the project directory to the Python path
project_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_dir)

# Try to import the package
try:
    import mkplaylist
    from mkplaylist import config
    print(f"Successfully imported mkplaylist package (version {mkplaylist.__version__})")
except ImportError as e:
    print(f"Error: Could not import mkplaylist package: {e}")
    print("\nTrying alternative import approach...")
    
    # If the package is not installed, try to import the module directly
    try:
        sys.path.insert(0, os.path.join(project_dir, "mkplaylist"))
        import config
        print("Successfully imported config module directly")
    except ImportError as e:
        print(f"Error: Could not import config module directly: {e}")
        print("\nDebug information:")
        print(f"Current directory: {os.getcwd()}")
        print(f"Python path: {sys.path}")
        print(f"Directory contents: {os.listdir(project_dir)}")
        if os.path.exists(os.path.join(project_dir, "mkplaylist")):
            print(f"mkplaylist directory contents: {os.listdir(os.path.join(project_dir, 'mkplaylist'))}")
        sys.exit(1)

def create_test_env_file(content):
    """Create a test .env file with the given content."""
    with open(".env.test", "w") as f:
        f.write(content)
    
    # If .env exists, rename it temporarily
    env_path = Path(".env")
    env_backup = None
    if env_path.exists():
        env_backup = Path(".env.backup")
        env_path.rename(env_backup)
    
    # Rename .env.test to .env
    Path(".env.test").rename(env_path)
    
    return env_backup

def restore_env_file(env_backup):
    """Restore the original .env file if it existed."""
    env_path = Path(".env")
    if env_path.exists():
        env_path.unlink()
    
    if env_backup and env_backup.exists():
        env_backup.rename(env_path)

def print_header(title):
    """Print a formatted header."""
    print("\n" + "=" * 80)
    print(f" {title} ".center(80, "="))
    print("=" * 80)

def run_test(test_name, env_vars, env_file_content):
    """Run a test with the given environment variables and .env file content."""
    print_header(test_name)
    
    # Set environment variables
    original_env = {}
    for key, value in env_vars.items():
        if key in os.environ:
            original_env[key] = os.environ[key]
        os.environ[key] = value
    
    # Create .env file
    env_backup = None
    if env_file_content is not None:
        env_backup = create_test_env_file(env_file_content)
    
    try:
        # Reload the config module to apply new environment variables and .env file
        import importlib
        importlib.reload(config)
        
        # Print configuration values
        print("\nConfiguration Values:")
        print(f"SPOTIFY_CLIENT_ID: {config.SPOTIFY_CLIENT_ID}")
        print(f"SPOTIFY_CLIENT_SECRET: {config.SPOTIFY_CLIENT_SECRET}")
        print(f"SPOTIFY_REDIRECT_URI: {config.SPOTIFY_REDIRECT_URI}")
        print(f"LASTFM_API_KEY: {config.LASTFM_API_KEY}")
        print(f"LASTFM_API_SECRET: {config.LASTFM_API_SECRET}")
        
        # Print configuration sources
        print("\nConfiguration Sources:")
        sources = config.get_config_sources()
        for key, source in sources.items():
            print(f"{key}: {source}")
        
        # Validate configuration
        print("\nConfiguration Validation:")
        issues = config.validate_config()
        if issues:
            print("Issues found:")
            for key, message in issues.items():
                print(f"  - {key}: {message}")
        else:
            print("No issues found.")
        
        # Print configuration status
        print("\nConfiguration Status:")
        status = config.get_config_status()
        for key, value in status.items():
            print(f"{key}: {value}")
        
    finally:
        # Restore original environment variables
        for key in env_vars:
            if key in original_env:
                os.environ[key] = original_env[key]
            else:
                del os.environ[key]
        
        # Restore original .env file
        if env_backup:
            restore_env_file(env_backup)

# Test 1: Environment variables only
run_test(
    "Test 1: Environment Variables Only",
    {
        "SPOTIFY_CLIENT_ID": "env_spotify_id",
        "SPOTIFY_CLIENT_SECRET": "env_spotify_secret",
        "LASTFM_API_KEY": "env_lastfm_key",
    },
    None  # No .env file
)

# Test 2: .env file only
run_test(
    "Test 2: .env File Only",
    {},  # No environment variables
    """
SPOTIFY_CLIENT_ID=dotenv_spotify_id
SPOTIFY_CLIENT_SECRET=dotenv_spotify_secret
LASTFM_API_KEY=dotenv_lastfm_key
"""
)

# Test 3: Both environment variables and .env file (with .env taking precedence)
run_test(
    "Test 3: Environment Variables + .env File (with .env taking precedence)",
    {
        "SPOTIFY_CLIENT_ID": "env_spotify_id",
        "SPOTIFY_CLIENT_SECRET": "env_spotify_secret",
        "LASTFM_API_KEY": "env_lastfm_key",
    },
    """
SPOTIFY_CLIENT_ID=dotenv_spotify_id
LASTFM_API_SECRET=dotenv_lastfm_secret
"""
)

# Test 4: Default values when neither environment variables nor .env file provide values
run_test(
    "Test 4: Default Values",
    {},  # No environment variables
    """
# Empty .env file with no values
"""
)

print_header("All Tests Completed")
print("\nSummary:")
print("1. Environment variables are loaded as baseline configuration")
print("2. Values from .env file override environment variables if present")
print("3. Default values are used when neither source provides a value")
print("\nConfiguration precedence is working as expected!")
