# Starfleet Protocols
import os
import logging
import importlib
import importlib.util

from typing import Any, Dict, Optional
from pathlib import Path

# Non-Federation Tech
from dotenv import load_dotenv

# Scotty in the Jefferies Tube
from .base import BaseServiceConfig


class MkPlaylistConfig:

  def __init__(
    self,
    args: Optional[Dict[str, Any]] = None,
    logger: Optional[logging.Logger] = None
  ):
    self.logger = logger or logging.getLogger(__name__)
    self.args = args or {}

    # Load .env file if it exists
    env_path = self.args.get('env_file', '.env')

    if Path(env_path).exists():
      load_dotenv(dotenv_path=env_path)
      self.logger.info(f"Loaded .env file from {env_path}")

    else:
      self.logger.debug(f"No .env file found at {env_path}")

    # Load built-in service modules
    self._load_builtin_services()

    # Load custom service modules if provided
    custom_service_path = self.args.get('custom_service_path')
    if custom_service_path:
      self._load_custom_services(custom_service_path)

  def _load_builtin_services(self) -> None:
    """Load built-in service configuration modules from modulename/config/services/."""
    services_dir = Path(__file__).parent / 'services'
    if not services_dir.exists():
      self.logger.warning(
        f"No built-in services directory found at {services_dir}"
      )
      return

    for service_file in services_dir.glob('*.py'):
      if service_file.stem.startswith('_'):
        continue

      service_name = service_file.stem

      try:
        module = importlib.import_module(
          f".services.{service_name}", package=__name__
        )
        config_class = getattr(
          module, f"{service_name.capitalize()}Config", None
        )

        if config_class and issubclass(
            config_class,
            BaseServiceConfig) and config_class != BaseServiceConfig:
          service_config = config_class(self.args, self.logger)
          setattr(self, service_name, service_config)
          self.logger.info(f"Loaded built-in service: {service_name}")

      except Exception as e:
        self.logger.error(f"Failed to load service {service_name}: {str(e)}")

  def _load_custom_services(self, custom_path: str) -> None:
    """Load custom service configuration modules from the specified path."""
    custom_dir = Path(custom_path)
    if not custom_dir.exists():
      self.logger.error(f"Custom service path {custom_path} does not exist")
      return

    for service_file in custom_dir.glob('*.py'):
      if service_file.stem.startswith('_'):
        continue

      service_name = service_file.stem

      try:
        spec = importlib.util.spec_from_file_location(
          service_name, service_file
        )

        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        config_class = getattr(
          module, f"{service_name.capitalize()}Config", None
        )

        if config_class and issubclass(
            config_class,
            BaseServiceConfig) and config_class != BaseServiceConfig:
          service_config = config_class(self.args, self.logger)
          setattr(self, service_name, service_config)
          self.logger.info(f"Loaded custom service: {service_name}")

      except Exception as e:
        self.logger.error(
          f"Failed to load custom service {service_name}: {str(e)}"
        )

  def get_config_value(self, key: str, default: Any = None) -> Any:
    """Retrieve a configuration value with precedence: args > .env > env vars."""
    if key in self.args:
      return self.args[key]
    return os.environ.get(key, default)
