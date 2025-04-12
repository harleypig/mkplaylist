
"""
Base configuration module for mkplaylist.

This module provides the base configuration class that service-specific
configurations will extend.
"""

import logging
import os
from pathlib import Path
from typing import Any, Dict, Optional, Type, TypeVar, Union, List, Callable, Tuple

from typing import Any, Dict, Optional, Type, TypeVar

from dotenv import load_dotenv

# Set up logging
logger = logging.getLogger(__name__)

# Type variable for the configuration class
T = TypeVar('T', bound='BaseConfig')

# Type definitions for configuration values
ConfigValue = Union[str, int, bool, Path, None]
ValidationRule = Callable[[Any], Tuple[bool, str]]
ValidationRules = Dict[str, List[ValidationRule]]

# Common validation rules
def required(value: Any) -> Tuple[bool, str]:
    """Validate that a value is not None or empty."""
    if value is None or (isinstance(value, str) and not value):
        return False, "Value is required and cannot be empty"
    return True, ""

def min_length(min_len: int) -> ValidationRule:
    """Create a validator that checks minimum string length."""
    def validator(value: str) -> Tuple[bool, str]:
        if not isinstance(value, str):
            return False, f"Expected string, got {type(value).__name__}"
        if len(value) < min_len:
            return False, f"Value must be at least {min_len} characters long"
        return True, ""
    return validator

def max_length(max_len: int) -> ValidationRule:
    """Create a validator that checks maximum string length."""
    def validator(value: str) -> Tuple[bool, str]:
        if not isinstance(value, str):
            return False, f"Expected string, got {type(value).__name__}"
        if len(value) > max_len:
            return False, f"Value must be at most {max_len} characters long"
        return True, ""
    return validator

def exact_length(length: int) -> ValidationRule:
    """Create a validator that checks exact string length."""
    def validator(value: str) -> Tuple[bool, str]:
        if not isinstance(value, str):
            return False, f"Expected string, got {type(value).__name__}"
        if len(value) != length:
            return False, f"Value must be exactly {length} characters long"
        return True, ""
    return validator

def pattern(regex: str, description: str) -> ValidationRule:
    """Create a validator that checks if a string matches a regex pattern."""
    import re
    compiled_regex = re.compile(regex)
    def validator(value: str) -> Tuple[bool, str]:
        if not isinstance(value, str):
            return False, f"Expected string, got {type(value).__name__}"
        if not compiled_regex.match(value):
            return False, f"Value must be {description}"
        return True, ""
    return validator

def is_positive(value: int) -> Tuple[bool, str]:
    """Validate that a value is a positive integer."""
    if not isinstance(value, int):
        return False, f"Expected integer, got {type(value).__name__}"
    if value <= 0:
        return False, "Value must be positive"
    return True, ""

def is_url(value: str) -> Tuple[bool, str]:
    """Validate that a value is a URL."""
    if not isinstance(value, str):
        return False, f"Expected string, got {type(value).__name__}"
    if not value.startswith(('http://', 'https://')):
        return False, "Value must be a valid URL starting with http:// or https://"
    return True, ""

def is_path(value: Any) -> Tuple[bool, str]:
    """Validate that a value is a Path object."""
    if not isinstance(value, Path):
        return False, f"Expected Path, got {type(value).__name__}"
    return True, ""

def path_exists(value: Path) -> Tuple[bool, str]:
    """Validate that a path exists."""
    if not isinstance(value, Path):
        return False, f"Expected Path, got {type(value).__name__}"
    if not value.exists():
        return False, f"Path {value} does not exist"
    return True, ""

def is_file(value: Path) -> Tuple[bool, str]:
    """Validate that a path is a file."""
    if not isinstance(value, Path):
        return False, f"Expected Path, got {type(value).__name__}"
    if not value.is_file():
        return False, f"Path {value} is not a file"
    return True, ""

def is_directory(value: Path) -> Tuple[bool, str]:
    """Validate that a path is a directory."""
    if not isinstance(value, Path):
        return False, f"Expected Path, got {type(value).__name__}"
    if not value.is_dir():
        return False, f"Path {value} is not a directory"
    return True, ""

def one_of(options: List[Any]) -> ValidationRule:
    """Create a validator that checks if a value is one of the given options."""
    def validator(value: Any) -> Tuple[bool, str]:
        if value not in options:
            return False, f"Value must be one of: {', '.join(str(o) for o in options)}"
        return True, ""
    return validator


class BaseConfig:
    """
    Base configuration class for mkplaylist.

    This class provides common functionality for all service-specific
    configurations, including environment variable loading and validation.
    """

    def __init__(self):
        """
        Initialize the base configuration.

        Stores original environment variables before loading .env file.
        """
        # Store original environment variables before loading .env
        self.env_vars = {key: value for key, value in os.environ.items()}

    @classmethod
    def load(cls: Type[T]) -> T:
        """
        Load configuration from environment variables and .env file.

        Returns:
            An instance of the configuration class.
        """
        # Load .env file which will override environment variables
        load_dotenv(override=True)
        
        # Create and return a new instance
        return cls()

    def get_env(self, key: str, default: Any = None) -> Any:
        """
        Get an environment variable.

        Args:
            key: The environment variable key.
            default: The default value if the key is not found.

        Returns:
            The value of the environment variable, or the default value.
        """
        return os.environ.get(key, default)

    def get_env_int(self, key: str, default: int) -> int:
        """
        Get an environment variable as an integer.

        Args:
            key: The environment variable key.
            default: The default value if the key is not found or cannot be converted.

        Returns:
            The value of the environment variable as an integer, or the default value.
        """
        value = self.get_env(key)
        if value is None:
            return default
        try:
            return int(value)
        except ValueError:
            logger.warning(f"Environment variable {key} is not a valid integer: {value}")
            return default

    def get_env_bool(self, key: str, default: bool) -> bool:
        """
        Get an environment variable as a boolean.

        Args:
            key: The environment variable key.
            default: The default value if the key is not found.

        Returns:
            The value of the environment variable as a boolean, or the default value.
        """
        value = self.get_env(key)
        if value is None:
            return default
        return value.lower() in ('true', 'yes', '1', 'y')

    def get_env_path(self, key: str, default: Optional[Path] = None) -> Optional[Path]:
        """
        Get an environment variable as a Path.

        Args:
            key: The environment variable key.
            default: The default value if the key is not found.

        Returns:
            The value of the environment variable as a Path, or the default value.
        """
        value = self.get_env(key)
        if value is None:
            return default
        return Path(value)

    def _validate_value(self, value: Any, rules: List[ValidationRule]) -> List[str]:
        """
        Validate a value against a list of validation rules.

        Args:
            value: The value to validate.
            rules: A list of validation rules to apply.

        Returns:
            A list of error messages. Empty if all rules pass.
        """
        errors = []
        for rule in rules:
            is_valid, error_message = rule(value)
            if not is_valid:
                errors.append(error_message)
        return errors

    def _validate_with_rules(self, values: Dict[str, Any], rules: ValidationRules) -> Dict[str, str]:
        """
        Validate a dictionary of values against a dictionary of validation rules.

        Args:
            values: A dictionary of values to validate.
            rules: A dictionary of validation rules to apply.

        Returns:
            A dictionary of validation issues, with keys as issue identifiers
            and values as error messages. Empty if all is valid.
        """
        issues = {}
        for key, value_rules in rules.items():
            if key in values:
                errors = self._validate_value(values[key], value_rules)
                if errors:
                    issues[key] = "; ".join(errors)
        return issues

    def validate(self) -> Dict[str, str]:
        """
        Validate the configuration and return any issues.

        This method should be overridden by subclasses to provide
        service-specific validation.

        Returns:
            Dict[str, str]: A dictionary of configuration issues, with keys as issue identifiers
                        and values as error messages. Empty if all is valid.
        """
        return {}

    def status(self) -> Dict[str, bool]:
        """
        Get the status of various configuration items.

        This method should be overridden by subclasses to provide
        service-specific status information.

        Returns:
            Dict[str, bool]: A dictionary with configuration items as keys and their status as boolean values.
                         True indicates the item is properly configured.
        """
        return {}

    def source(self, env_var_name: str) -> str:
        """
        Get information about where a configuration value is coming from.

        Args:
            env_var_name: The environment variable name.

        Returns:
            str: A string indicating the source of the configuration value.
                 Possible sources: "Environment variable", ".env file",
                 ".env file (overriding environment variable)", or "Default value".
        """
        # Check if .env file exists
        dotenv_path = Path('.env')
        dotenv_exists = dotenv_path.exists()

        # Get original environment variables (before .env was loaded)
        original_env = self.env_vars

        if not dotenv_exists:
            return "Environment variable" if env_var_name in original_env else "Default value"

        # If .env exists, check if value changed after loading .env
        if env_var_name in original_env:
            current_value = os.environ.get(env_var_name)
            original_value = original_env.get(env_var_name)

            if current_value != original_value:
                return ".env file (overriding environment variable)"
            return "Environment variable"

        if env_var_name in os.environ:
            return ".env file"

        return "Default value"

    def data_dir(self) -> Path:
        """
        Get the data directory for the application.

        Follows XDG Base Directory Specification on Unix/Linux/Mac systems,
        using XDG_DATA_HOME environment variable with fallback to ~/.local/share.
        On Windows, uses APPDATA environment variable.

        Returns:
            Path: The data directory path, created if it doesn't exist
        """
        if os.name == 'nt':                                    # Windows
            data_dir = Path(os.environ.get('APPDATA', '')) / 'mkplaylist'
        else:                                                  # Unix/Linux/Mac
            data_dir = Path(
                os.environ.get('XDG_DATA_HOME',
                            Path.home() / '.local' / 'share')
            ) / 'mkplaylist'

        # Create directory if it doesn't exist
        data_dir.mkdir(parents=True, exist_ok=True)
        return data_dir

    def config_dir(self) -> Path:
        """
        Get the configuration directory for the application.

        Follows XDG Base Directory Specification on Unix/Linux/Mac systems,
        using XDG_CONFIG_HOME environment variable with fallback to ~/.config.
        On Windows, uses APPDATA environment variable with a 'config' subdirectory.

        Returns:
            Path: The configuration directory path, created if it doesn't exist
        """
        if os.name == 'nt':                          # Windows
            config_dir = Path(
                os.environ.get('APPDATA', '')
            ) / 'mkplaylist' / 'config'
        else:                                        # Unix/Linux/Mac
            config_dir = Path(
                os.environ.get('XDG_CONFIG_HOME',
                            Path.home() / '.config')
            ) / 'mkplaylist'

        # Create directory if it doesn't exist
        config_dir.mkdir(parents=True, exist_ok=True)
        return config_dir

    def cache_dir(self) -> Path:
        """
        Get the cache directory for the application.

        Follows XDG Base Directory Specification on Unix/Linux/Mac systems,
        using XDG_CACHE_HOME environment variable with fallback to ~/.cache.
        On Windows, uses LOCALAPPDATA environment variable with a 'cache' subdirectory.

        Returns:
            Path: The cache directory path, created if it doesn't exist
        """
        if os.name == 'nt':                          # Windows
            cache_dir = Path(
                os.environ.get('LOCALAPPDATA', '')
            ) / 'mkplaylist' / 'cache'
        else:                                        # Unix/Linux/Mac
            cache_dir = Path(
                os.environ.get('XDG_CACHE_HOME',
                            Path.home() / '.cache')
            ) / 'mkplaylist'

        # Create directory if it doesn't exist
        cache_dir.mkdir(parents=True, exist_ok=True)
        return cache_dir

    def state_dir(self) -> Path:
        """
        Get the state directory for the application.

        Follows XDG Base Directory Specification on Unix/Linux/Mac systems,
        using XDG_STATE_HOME environment variable with fallback to ~/.local/state.
        On Windows, uses LOCALAPPDATA environment variable with a 'state' subdirectory.

        This directory is used for persistent application state data like authentication tokens.

        Returns:
            Path: The state directory path, created if it doesn't exist
        """
        if os.name == 'nt':                                    # Windows
            state_dir = Path(
                os.environ.get('LOCALAPPDATA', '')
            ) / 'mkplaylist' / 'state'
        else:                                                  # Unix/Linux/Mac
            state_dir = Path(
                os.environ.get('XDG_STATE_HOME',
                            Path.home() / '.local' / 'state')
            ) / 'mkplaylist'

        # Create directory if it doesn't exist
        state_dir.mkdir(parents=True, exist_ok=True)
        return state_dir

    def db_path(self) -> Path:
        """
        Get the path to the SQLite database file.

        Checks for a custom path in the MKPLAYLIST_DB_PATH environment variable.
        If not set, uses a default path in the data directory.

        Returns:
            Path: The database file path
        """
        # Check for custom path in environment variable
        custom_path = os.environ.get('MKPLAYLIST_DB_PATH')
        if custom_path:
            return Path(custom_path)

        # Default path in data directory
        default_path = self.data_dir() / 'mkplaylist.db'
        return default_path
