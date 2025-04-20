# Starfleet Protocols
import logging

from typing import Any, Dict, Optional


class BaseServiceConfig:

  def __init__(self, args: Dict[str, Any], logger: logging.Logger):
    self.args = args
    self.logger = logger
    self._load_config()

  def _load_config(self) -> None:
    """Load and validate configuration for the service. Must be implemented by subclasses."""
    raise NotImplementedError("Subclasses must implement _load_config")

  def validate(self, key: str, value: Any) -> bool:
    """Validate a configuration value. Can be overridden by subclasses."""
    if value is None:
      self.logger.warning(f"Configuration value for {key} is None")
      return False
    return True

  def _set_config_attr(self, key: str, value: Any) -> None:
    """Set a configuration attribute with validation."""
    if self.validate(key, value):
      setattr(self, key, value)
    else:
      self.logger.error(f"Invalid configuration for {key}: {value}")
