# Configuration Architecture

The mkplaylist configuration system is designed to be modular, extensible, and
type-safe. This document explains the architecture of the configuration
system, how to add new service configurations, and how to use the
configuration API.

## Overview

The configuration system is organized as follows:

```
mkplaylist/
  config/
    __init__.py       # Main configuration class and exports
    base.py           # Base configuration functionality
    spotify.py        # Spotify-specific configuration
    lastfm.py         # Last.fm-specific configuration
```

The system follows these design principles:

1. **Modularity**: Each service has its own configuration module
2. **Type Safety**: Configuration values have defined types and validation rules
3. **Extensibility**: New services can be added easily by creating new modules
4. **Validation**: Comprehensive validation rules ensure configuration correctness
5. **Transparency**: Users can see where configuration values come from

## Configuration Loading

Configuration values are loaded from two sources, in order of precedence:

1. Environment variables
2. `.env` file

The `.env` file will override environment variables if both are present. This
allows users to set up their configuration in a way that works best for their
workflow.

## Base Configuration

The `BaseConfig` class in `mkplaylist/config/base.py` provides common
functionality for all service-specific configurations:

- Loading environment variables and `.env` files
- Type conversion methods (`get_env_int`, `get_env_bool`, `get_env_path`)
- Directory path methods following XDG Base Directory Specification
- Validation framework
- Source tracking (where configuration values come from)

## Service-Specific Configurations

Each service has its own configuration class that extends `BaseConfig`:

- `SpotifyConfig` in `spotify.py` for Spotify API credentials
- `LastfmConfig` in `lastfm.py` for Last.fm API credentials

These classes define service-specific configuration values, validation rules,
and status methods.

## Main Configuration

The `MkPlaylistConfig` class in `__init__.py` brings everything together:

- Loads service-specific configurations
- Provides access to all configuration values
- Combines validation and status results from all services
- Exports common methods for easier access

## Adding a New Service Configuration

To add a new service configuration:

1. Create a new file in the `mkplaylist/config/` directory (e.g., `deezer.py`)
2. Define a new configuration class that extends `BaseConfig`
3. Implement the required methods: `validate()`, `status()`, and `sources()`
4. Update the `MkPlaylistConfig` class to load and expose the new configuration

Here's an example of adding a new service configuration for Deezer:

```python
# mkplaylist/config/deezer.py
from typing import Dict
from mkplaylist.config.base import BaseConfig, ValidationRules, required

class DeezerConfig(BaseConfig):
    def __init__(self):
        super().__init__()

        # Load Deezer API credentials
        self.API_KEY = self.get_env('DEEZER_API_KEY', '')
        self.APP_ID = self.get_env('DEEZER_APP_ID', '')
        self.SECRET = self.get_env('DEEZER_SECRET', '')

        # Define validation rules
        self.validation_rules: ValidationRules = {
            'API_KEY': [required],
            'APP_ID': [required],
            'SECRET': [required],
        }

    def validate(self) -> Dict[str, str]:
        # Implementation similar to other service configs
        # ...

    def status(self) -> Dict[str, bool]:
        # Implementation similar to other service configs
        # ...

    def sources(self) -> Dict[str, str]:
        # Implementation similar to other service configs
        # ...
```

Then update the `MkPlaylistConfig` class:

```python
# In mkplaylist/config/__init__.py
from mkplaylist.config.deezer import DeezerConfig

class MkPlaylistConfig(BaseConfig):
    def __init__(self):
        super().__init__()

        # Load service-specific configurations
        self.spotify = SpotifyConfig()
        self.lastfm = LastfmConfig()
        self.deezer = DeezerConfig()  # Add the new service

        # ... rest of the implementation
```

## Using the Configuration API

The configuration API is designed to be simple and intuitive. Here are some examples of how to use it:

### Accessing Configuration Values

```python
from mkplaylist.config import config

# Access Spotify configuration
spotify_client_id = config.spotify.CLIENT_ID
spotify_client_secret = config.spotify.CLIENT_SECRET

# Access Last.fm configuration
lastfm_api_key = config.lastfm.API_KEY
lastfm_username = config.lastfm.USERNAME

# Access application settings
default_sync_days = config.DEFAULT_SYNC_DAYS
log_level = config.LOG_LEVEL
```

### Accessing Directory Paths

```python
from mkplaylist.config import data_dir, config_dir, cache_dir, state_dir, db_path

# Get directory paths
data_directory = data_dir()
config_directory = config_dir()
cache_directory = cache_dir()
state_directory = state_dir()

# Get database path
database_path = db_path()
```

### Validating Configuration

```python
from mkplaylist.config import validate

# Check if configuration is valid
issues = validate()
if issues:
    print("Configuration issues found:")
    for key, message in issues.items():
        print(f"  - {key}: {message}")
else:
    print("Configuration is valid!")
```

### Checking Configuration Status

```python
from mkplaylist.config import status

# Get configuration status
status_dict = status()
for key, value in status_dict.items():
    print(f"{key}: {'OK' if value else 'Not configured'}")
```

### Checking Configuration Sources

```python
from mkplaylist.config import sources

# Get configuration sources
sources_dict = sources()
for key, source in sources_dict.items():
    print(f"{key}: {source}")
```

## Validation System

The validation system is designed to be flexible and extensible. It consists of:

1. **Validation Rules**: Functions that check if a value meets certain criteria
2. **Validation Framework**: Methods to apply rules to configuration values
3. **User-Friendly Messages**: Clear error messages for configuration issues

### Validation Rules

Validation rules are functions that take a value and return a tuple of `(bool, str)`:
- `bool`: Whether the validation passed (`True`) or failed (`False`)
- `str`: An error message if validation failed, empty string otherwise

The base configuration module provides common validation rules:

- `required`: Checks if a value is not None or empty
- `min_length`: Checks if a string has a minimum length
- `max_length`: Checks if a string has a maximum length
- `exact_length`: Checks if a string has an exact length
- `pattern`: Checks if a string matches a regex pattern
- `is_positive`: Checks if a value is a positive integer
- `is_url`: Checks if a value is a valid URL
- `is_path`: Checks if a value is a Path object
- `path_exists`: Checks if a path exists
- `is_file`: Checks if a path is a file
- `is_directory`: Checks if a path is a directory
- `one_of`: Checks if a value is one of the given options

Service-specific modules can define their own validation rules:

- `is_valid_client_id`: Checks if a value is a valid Spotify Client ID
- `is_valid_client_secret`: Checks if a value is a valid Spotify Client Secret
- `is_valid_redirect_uri`: Checks if a value is a valid Spotify Redirect URI
- `is_valid_api_key`: Checks if a value is a valid Last.fm API Key
- `is_valid_api_secret`: Checks if a value is a valid Last.fm API Secret
- `is_valid_username`: Checks if a value is a valid Last.fm username

### Adding Custom Validation Rules

To add a custom validation rule, define a function that takes a value and returns a tuple of `(bool, str)`:

```python
```python
def is_valid_email(value: str) -> Tuple[bool, str]:
    """Validate that a value is a valid email address."""
    if not value:
        return False, "Email cannot be empty"
    if "@" not in value or "." not in value:
        return False, "Invalid email format"
    return True, ""
```

```

Then add it to the validation rules for a configuration value:

```python
```python
self.validation_rules: ValidationRules = {
    'EMAIL': [required, is_valid_email],
}
```

```

### Applying Validation Rules

The `_validate_value` method applies a list of validation rules to a value:

```python
```python
errors = self._validate_value(value, rules)
```

```

The `_validate_with_rules` method applies a dictionary of validation rules to a dictionary of values:

```python
```python
issues = self._validate_with_rules(values, self.validation_rules)
```

### Validation Rule Design Pattern

The configuration system uses a design pattern where validation rules are defined as standalone functions outside of the configuration classes. This approach offers several important benefits:

#### 1. Separation of Concerns

By defining validation rules as standalone functions outside of classes:

- **Clear Responsibility**: Each validation rule has a single, well-defined responsibility
- **Focused Logic**: Rules contain only validation logic, not configuration management
- **Independent Testing**: Rules can be tested independently of the configuration classes
- **Reduced Complexity**: Configuration classes focus on managing values, not validation details

#### 2. Reusability and Composition

Standalone validation rules enable powerful reuse patterns:

- **Cross-Service Reuse**: Common rules like `required` or `exact_length` can be used across different service configurations
- **Rule Composition**: Multiple rules can be combined to create complex validation logic
- **Rule Factories**: Higher-order functions like `min_length` can generate specialized rules
- **Mix and Match**: Different combinations of rules can be applied to different configuration values

For example, the same `exact_length(32)` rule can be used for both Spotify Client IDs and Last.fm API Keys:

```python
# In spotify.py
self.validation_rules = {
    'CLIENT_ID': [required, exact_length(32), is_alphanumeric],
    # ...
}

# In lastfm.py
self.validation_rules = {
    'API_KEY': [required, exact_length(32), is_hexadecimal],
    # ...
}
```

#### 3. Extensibility

The pattern makes it easy to extend the validation system:

- **Add New Rules**: New validation rules can be added without modifying existing classes
- **Service-Specific Rules**: Each service can define its own specialized validation rules
- **Third-Party Extensions**: External modules can provide additional validation rules
- **Progressive Enhancement**: Validation can be enhanced over time without breaking changes

#### 4. Declarative Configuration

The approach enables a declarative style for defining validation requirements:

```python
self.validation_rules = {
    'CLIENT_ID': [required, exact_length(32), is_alphanumeric],
    'CLIENT_SECRET': [required, exact_length(32), is_alphanumeric],
    'REDIRECT_URI': [required, is_url],
}
```

This declarative style makes it immediately clear what validation requirements apply to each configuration value, improving code readability and maintainability.

#### 5. Practical Examples

Here are some examples of how this pattern enables powerful validation capabilities:

**Example 1: Combining Multiple Rules**

```python
# Define validation rules for a configuration value
self.validation_rules = {
    'USERNAME': [
        required,                                  # Must not be empty
        min_length(3),                             # Must be at least 3 characters
        max_length(20),                            # Must be at most 20 characters
        pattern(r'^[a-zA-Z0-9_]+$', 'alphanumeric with underscores')  # Must match pattern
    ],
}
```

**Example 2: Creating Custom Rule Combinations**

```python
# Create a composite validation rule
def is_valid_password(value: str) -> Tuple[bool, str]:
    """Validate that a value is a valid password."""
    # Apply multiple validation checks in sequence
    for rule in [min_length(8), has_uppercase, has_lowercase, has_digit, has_special_char]:
        is_valid, error = rule(value)
        if not is_valid:
            return False, error
    return True, ""

# Use the composite rule
self.validation_rules = {
    'PASSWORD': [required, is_valid_password],
}
```

**Example 3: Conditional Validation**

```python
def requires_if(condition_fn, rule):
    """Apply a validation rule only if a condition is met."""
    def validator(value):
        if condition_fn():
            return rule(value)
        return True, ""
    return validator

# Use conditional validation
self.validation_rules = {
    'API_KEY': [
        requires_if(lambda: self.API_ENABLED, required),
        requires_if(lambda: self.API_ENABLED, exact_length(32))
    ],
}
```

This design pattern creates a flexible, extensible validation system that can grow with the application's needs while maintaining clean, maintainable code.

```

## CLI Commands

The configuration system includes CLI commands for viewing and validating configuration:

```bash
# Show configuration status
mkplaylist config status

# Validate configuration
mkplaylist config validate

# Show configuration status in JSON format
mkplaylist config status --format json

# Validate configuration in JSON format
mkplaylist config validate --format json
```

These commands provide a convenient way to check the configuration status and identify any issues.

## Best Practices

When working with the configuration system, follow these best practices:

1. **Use Environment Variables**: Use environment variables for configuration values that change between environments
2. **Use `.env` File**: Use a `.env` file for local development
3. **Validate Early**: Validate configuration at startup to catch issues early
4. **Add Validation Rules**: Add validation rules for all configuration values
5. **Document Configuration**: Document all configuration values and their purpose
6. **Use Type Hints**: Use type hints for all configuration values
7. **Follow Naming Conventions**: Use consistent naming conventions for environment variables
