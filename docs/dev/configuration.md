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

## Automatic Service Configuration Loading

The configuration system includes an automatic service discovery and loading
mechanism that makes it easy to add new service configurations without
modifying the main configuration class.

### How It Works

1. **Service Discovery**: When the main configuration class is initialized, it
   scans the `mkplaylist/config` package for modules that define service
   configuration classes (subclasses of `ServiceConfig`).

2. **Registration**: Each discovered service configuration class is registered
   in a central registry.

3. **Instantiation**: The main configuration class creates instances of all
   registered service configurations and makes them available both as
   attributes (for backward compatibility) and through lookup methods.

This approach allows you to add new service configurations simply by creating
a new module in the `mkplaylist/config` directory that defines a class
extending `ServiceConfig`.

### Key Components

- **ServiceConfig Class**: An abstract base class that defines the interface for service configurations.
- **Service Discovery**: Functions that scan the package for service configuration classes.
- **Service Registry**: A dictionary that stores service configuration classes by name.
- **Dynamic Loading**: Code that creates instances of registered service configurations.

### Benefits

- **Extensibility**: Add new services without modifying existing code
- **Modularity**: Each service has its own self-contained configuration module
- **Discoverability**: Services are automatically discovered and loaded
- **Consistency**: All services follow the same interface and patterns

## Adding a New Service Configuration

To add a new service configuration:

1. Create a new file in the `mkplaylist/config/` directory (e.g., `deezer.py`)
2. Define a new configuration class that extends `ServiceConfig`
3. Implement the required methods: `validate()`, `status()`, and `sources()`
4. Implement the required `service_name` property
5. Define any service-specific validation rules in the same file

The new service will be automatically discovered and loaded by the main configuration class. You don't need to modify any other files.

Here's an example of adding a new service configuration for Deezer:

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

#### 5. Service-Specific Organization

The pattern encourages organizing validation rules by service:

- Common validation rules are defined in `base.py`
- Service-specific validation rules are defined in their respective service modules

This organization ensures that:

```python
# In spotify.py
def is_valid_client_id(value: str) -> Tuple[bool, str]:
    """Spotify-specific validation for client IDs."""
    # ...

# In lastfm.py
def is_valid_api_key(value: str) -> Tuple[bool, str]:
    """Last.fm-specific validation for API keys."""
    # ...

# In deezer.py
# mkplaylist/config/deezer.py
from typing import Dict, Tuple
from mkplaylist.config.base import ServiceConfig, ValidationRules, required, is_url

# Deezer-specific validation rules
def is_valid_app_id(value: str) -> Tuple[bool, str]:
    """Deezer-specific validation for app IDs."""
    """Validate that a value is a valid Deezer Application ID."""
    if not value:
        return False, "Deezer Application ID cannot be empty"
    try:
        app_id = int(value)
        if app_id <= 0:
            return False, "Deezer Application ID must be a positive integer"
        return True, ""
    except ValueError:
        return False, "Deezer Application ID must be a valid integer"

class DeezerConfig(ServiceConfig):
    """
    Deezer configuration class for mkplaylist.
    """
    
    @property
    def service_name(self) -> str:
        """Get the name of the service."""
        return 'deezer'

    def __init__(self):
        super().__init__()

        # Define validation rules using both common and service-specific rules
        # Load Deezer API credentials
        self.APP_ID = self.get_env('DEEZER_APP_ID', '')
        self.APP_SECRET = self.get_env('DEEZER_APP_SECRET', '')
        self.REDIRECT_URI = self.get_env(
            'DEEZER_REDIRECT_URI', 'http://localhost:8888/callback'
        )

        # Define validation rules
        self.validation_rules: ValidationRules = {
            'CLIENT_ID': [required, is_valid_client_id],
            # ...
            'APP_ID': [required, is_valid_app_id],
            'APP_SECRET': [required],
            'REDIRECT_URI': [required, is_url],
        }

```

When adding a new service, follow this pattern by defining any service-specific validation rules in the service's configuration module.

    def validate(self) -> Dict[str, str]:
        # Implementation similar to other service configs
        # ...
        pass

    def status(self) -> Dict[str, bool]:
        # Implementation similar to other service configs
        # ...
        pass

    def sources(self) -> Dict[str, str]:
        # Implementation similar to other service configs
        # ...
        pass
```

Note how the service-specific validation rule `is_valid_app_id` is defined in the same file as the `DeezerConfig` class. This keeps all Deezer-specific validation logic contained within the Deezer configuration module.
```

### Required Components

Every service configuration class must:

1. **Extend ServiceConfig**: Inherit from the `ServiceConfig` base class
2. **Define service_name**: Implement the `service_name` property to return a unique name
3. **Implement Required Methods**: Provide implementations for `validate()`, `status()`, and `sources()`
4. **Define Validation Rules**: Set up appropriate validation rules for configuration values

### Naming Conventions

- **Module Name**: Should match the service name (e.g., `deezer.py` for Deezer)
- **Class Name**: Should be the capitalized service name followed by "Config" (e.g., `DeezerConfig`)
- **Service Name**: Should be lowercase and match the module name (e.g., `'deezer'`)
- **Environment Variables**: Should be uppercase and prefixed with the service name (e.g., `DEEZER_APP_ID`)

### Accessing Service Configurations

Once a service configuration is loaded, it can be accessed in several ways:

```python
from mkplaylist.config import config

# Direct attribute access (for backward compatibility)
deezer_app_id = config.deezer.APP_ID

# Using get_service method
deezer_config = config.get_service('deezer')
deezer_app_id = deezer_config.APP_ID if deezer_config else None

# Getting all services
all_services = config.get_services()
service_names = config.get_service_names()
```

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
def is_valid_email(value: str) -> Tuple[bool, str]:
    """Validate that a value is a valid email address."""
    if not value:
        return False, "Email cannot be empty"
    if "@" not in value or "." not in value:
        return False, "Invalid email format"
    return True, ""
```

Then add it to the validation rules for a configuration value:

```python
self.validation_rules: ValidationRules = {
    'EMAIL': [required, is_valid_email],
}
```

### Applying Validation Rules

The `_validate_value` method applies a list of validation rules to a value:

```python
errors = self._validate_value(value, rules)
```

The `_validate_with_rules` method applies a dictionary of validation rules to a dictionary of values:

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
```

By placing service-specific validation rules in their respective service modules:

1. Each service module is self-contained with all its validation logic
2. Adding a new service doesn't require modifying existing modules
3. Service-specific validation rules can be easily found and maintained
4. The codebase remains modular and follows the principle of separation of concerns

#### 6. Practical Examples
When adding a new service, follow this pattern by defining any service-specific validation rules in the service's configuration module.

    def validate(self) -> Dict[str, str]:
        # Implementation similar to other service configs
        # ...
        pass

    def status(self) -> Dict[str, bool]:
        # Implementation similar to other service configs
        # ...
        pass

    def sources(self) -> Dict[str, str]:
        # Implementation similar to other service configs
        # ...
        pass
```

Note how the service-specific validation rule `is_valid_app_id` is defined in the same file as the `DeezerConfig` class. This keeps all Deezer-specific validation logic contained within the Deezer configuration module.
```

### Required Components

Every service configuration class must:

1. **Extend ServiceConfig**: Inherit from the `ServiceConfig` base class
2. **Define service_name**: Implement the `service_name` property to return a unique name
3. **Implement Required Methods**: Provide implementations for `validate()`, `status()`, and `sources()`
4. **Define Validation Rules**: Set up appropriate validation rules for configuration values

### Naming Conventions

- **Module Name**: Should match the service name (e.g., `deezer.py` for Deezer)
- **Class Name**: Should be the capitalized service name followed by "Config" (e.g., `DeezerConfig`)
- **Service Name**: Should be lowercase and match the module name (e.g., `'deezer'`)
- **Environment Variables**: Should be uppercase and prefixed with the service name (e.g., `DEEZER_APP_ID`)

### Accessing Service Configurations

Once a service configuration is loaded, it can be accessed in several ways:

```python
from mkplaylist.config import config

# Direct attribute access (for backward compatibility)
deezer_app_id = config.deezer.APP_ID

# Using get_service method
deezer_config = config.get_service('deezer')
deezer_app_id = deezer_config.APP_ID if deezer_config else None

# Getting all services
all_services = config.get_services()
service_names = config.get_service_names()
```

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
def is_valid_email(value: str) -> Tuple[bool, str]:
    """Validate that a value is a valid email address."""
    if not value:
        return False, "Email cannot be empty"
    if "@" not in value or "." not in value:
        return False, "Invalid email format"
    return True, ""
```

Then add it to the validation rules for a configuration value:

```python
self.validation_rules: ValidationRules = {
    'EMAIL': [required, is_valid_email],
}
```

### Applying Validation Rules

The `_validate_value` method applies a list of validation rules to a value:

```python
errors = self._validate_value(value, rules)
```

The `_validate_with_rules` method applies a dictionary of validation rules to a dictionary of values:

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

Example 1: Combining Multiple Rules

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

Example 2: Creating Custom Rule Combinations

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

Example 3: Conditional Validation

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

## CLI Commands

The configuration system includes CLI commands for viewing and validating configuration:


## Testing Service Configurations

When adding a new service configuration, it's important to test that it's properly discovered and loaded by the automatic loading system. Here are some ways to test your new service configuration:

### Using the CLI

The simplest way to test a new service configuration is to use the CLI commands:

```bash
# Check if the new service appears in the status output
# Show configuration status
mkplaylist config_cmd status

# Validate the new service configuration
# Validate configuration
mkplaylist config_cmd validate
```

If your service is properly discovered and loaded, it will appear in the status output with its configuration items.

### Using the API

You can also test the service configuration programmatically:

```python
from mkplaylist.config import config, get_service_names

# Check if the service is in the list of loaded services
service_names = get_service_names()
assert 'deezer' in service_names

# Get the service configuration
deezer_config = config.get_service('deezer')
assert deezer_config is not None

# Check if the service is accessible as an attribute
assert hasattr(config, 'deezer')
assert config.deezer is deezer_config

# Test validation
issues = deezer_config.validate()
deezer_app_id = deezer_config.APP_ID if deezer_config else None

# Getting all services
all_services = config.get_services()
service_names = config.get_service_names()
```

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
    print("Validation issues:", issues)
    print("Configuration issues found:")
    for key, message in issues.items():
        print(f"  - {key}: {message}")
else:
    print("Validation passed!")

# Test status
status = deezer_config.status()
print("Status:", status)

# Test sources
sources = deezer_config.sources()
print("Sources:", sources)
```

### Troubleshooting

If your service configuration is not being discovered and loaded, check the following:

1. **Module Location**: Make sure the module is in the `mkplaylist/config` directory
2. **Class Inheritance**: Ensure the class extends `ServiceConfig`
3. **Service Name**: Check that the `service_name` property returns a unique name
4. **Required Methods**: Verify that all required methods are implemented
5. **Import Errors**: Look for any import errors in the module

You can enable debug logging to see more information about the service discovery process:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

This will show log messages about which modules are being scanned and which service configurations are being registered.
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
def is_valid_email(value: str) -> Tuple[bool, str]:
    """Validate that a value is a valid email address."""
    if not value:
        return False, "Email cannot be empty"
    if "@" not in value or "." not in value:
        return False, "Invalid email format"
    return True, ""
```

Then add it to the validation rules for a configuration value:

```python
self.validation_rules: ValidationRules = {
    'EMAIL': [required, is_valid_email],
}
```

### Applying Validation Rules

The `_validate_value` method applies a list of validation rules to a value:

```python
errors = self._validate_value(value, rules)
```

The `_validate_with_rules` method applies a dictionary of validation rules to a dictionary of values:

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

Example 1: Combining Multiple Rules

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

Example 2: Creating Custom Rule Combinations

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

Example 3: Conditional Validation

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

## CLI Commands

The configuration system includes CLI commands for viewing and validating configuration:


```bash
# Show configuration status
mkplaylist config_cmd status

# Validate configuration
mkplaylist config_cmd validate

# Show configuration status in JSON format
mkplaylist config_cmd status --format json

# Validate configuration in JSON format
mkplaylist config_cmd validate --format json
```

These commands provide a convenient way to check the configuration status and identify any issues. They automatically include all discovered service configurations, so any new services you add will be included in the output without requiring changes to the CLI code.

### Example Output

When you run the status command with a Deezer configuration added:

```
Configuration Status:
=====================

Spotify:
  ✓ client_id_configured
  ✓ client_secret_configured
  ✓ redirect_uri_configured

Lastfm:
  ✓ api_key_configured
  ✓ api_secret_configured
  ✓ username_configured

Deezer:
  ✓ app_id_configured
  ✓ app_secret_configured
  ✓ redirect_uri_configured

General:
  ✓ spotify_configured
  ✓ lastfm_configured
  ✓ deezer_configured
  ✓ database_path_set
  ✓ default_sync_days_valid
  ✓ log_level_valid

Configuration Sources:
=====================
  SPOTIFY_CLIENT_ID: .env file
  SPOTIFY_CLIENT_SECRET: .env file
  SPOTIFY_REDIRECT_URI: .env file
  LASTFM_API_KEY: .env file
  LASTFM_API_SECRET: .env file
  LASTFM_USERNAME: .env file
  DEEZER_APP_ID: .env file
  DEEZER_APP_SECRET: .env file
  DEEZER_REDIRECT_URI: .env file
  MKPLAYLIST_DEFAULT_SYNC_DAYS: Default value
  LOG_LEVEL: Default value
  MKPLAYLIST_DB_PATH: Default value

Configuration Paths:
==================
  Data directory: /home/user/.local/share/mkplaylist
  Config directory: /home/user/.config/mkplaylist
  Cache directory: /home/user/.cache/mkplaylist
  State directory: /home/user/.local/state/mkplaylist
  Database path: /home/user/.local/share/mkplaylist/mkplaylist.db

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

