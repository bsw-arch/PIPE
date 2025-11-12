"""Configuration loader for PIPE domain bots."""

import os
import yaml
import json
from typing import Dict, Any
from pathlib import Path


class ConfigLoader:
    """Load and manage configuration from multiple sources."""

    def __init__(self, config_dir: str = "./config"):
        """
        Initialize configuration loader.

        Args:
            config_dir: Directory containing configuration files
        """
        self.config_dir = Path(config_dir)
        self.config: Dict[str, Any] = {}

    def load_from_file(self, filename: str) -> Dict[str, Any]:
        """
        Load configuration from a file.

        Args:
            filename: Configuration filename

        Returns:
            Configuration dictionary
        """
        filepath = self.config_dir / filename

        if not filepath.exists():
            raise FileNotFoundError(f"Configuration file not found: {filepath}")

        with open(filepath, 'r') as f:
            if filename.endswith('.yaml') or filename.endswith('.yml'):
                return yaml.safe_load(f)
            elif filename.endswith('.json'):
                return json.load(f)
            else:
                raise ValueError(f"Unsupported configuration format: {filename}")

    def load_from_env(self, prefix: str = "PIPE_") -> Dict[str, Any]:
        """
        Load configuration from environment variables.

        Args:
            prefix: Environment variable prefix

        Returns:
            Configuration dictionary from environment
        """
        config = {}
        for key, value in os.environ.items():
            if key.startswith(prefix):
                # Remove prefix and convert to lowercase
                config_key = key[len(prefix):].lower()
                config[config_key] = value

        return config

    def merge_configs(self, *configs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Merge multiple configuration dictionaries.

        Later configs override earlier ones.

        Args:
            *configs: Configuration dictionaries to merge

        Returns:
            Merged configuration
        """
        merged = {}
        for config in configs:
            self._deep_merge(merged, config)

        return merged

    def _deep_merge(self, base: Dict, update: Dict) -> None:
        """
        Deep merge update dict into base dict.

        Args:
            base: Base dictionary (modified in place)
            update: Update dictionary
        """
        for key, value in update.items():
            if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                self._deep_merge(base[key], value)
            else:
                base[key] = value

    def load(self, config_file: str = "config.yaml", use_env: bool = True) -> Dict[str, Any]:
        """
        Load complete configuration.

        Args:
            config_file: Main configuration file
            use_env: Whether to load from environment variables

        Returns:
            Complete configuration dictionary
        """
        configs = []

        # Load from file
        try:
            file_config = self.load_from_file(config_file)
            configs.append(file_config)
        except FileNotFoundError:
            pass  # File is optional

        # Load from environment
        if use_env:
            env_config = self.load_from_env()
            if env_config:
                configs.append(env_config)

        # Merge all configs
        self.config = self.merge_configs(*configs) if configs else {}

        return self.config

    def get(self, key: str, default: Any = None) -> Any:
        """
        Get a configuration value.

        Args:
            key: Configuration key (supports dot notation)
            default: Default value if key not found

        Returns:
            Configuration value
        """
        keys = key.split('.')
        value = self.config

        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
                if value is None:
                    return default
            else:
                return default

        return value


def load_config(config_file: str = "config.yaml", config_dir: str = "./config") -> Dict[str, Any]:
    """
    Convenience function to load configuration.

    Args:
        config_file: Configuration filename
        config_dir: Configuration directory

    Returns:
        Configuration dictionary
    """
    loader = ConfigLoader(config_dir)
    return loader.load(config_file)
