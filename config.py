# path: aida/config.py
# title: Configuration Manager
# role: Handles loading and providing application configuration from a YAML file.

import yaml
from pathlib import Path
from typing import Dict, Any

class Config:
    """
    Loads and provides access to application configuration settings.
    """
    def __init__(self, config_path: str):
        """
        Initializes the Config object by loading a YAML file.

        Args:
            config_path: The path to the YAML configuration file.
        
        Raises:
            FileNotFoundError: If the config file does not exist.
            TypeError: If the provided path is not a valid path-like object.
        """
        if not isinstance(config_path, (str, Path)):
            raise TypeError(f"Expected a path, but got {type(config_path)}")

        path = Path(config_path)
        if not path.exists():
            raise FileNotFoundError(f"Config file not found at: {path}")

        with open(path, 'r', encoding='utf-8') as f:
            self._data = yaml.safe_load(f)

    def get(self, key: str, default: Any = None) -> Any:
        """
        Retrieves a configuration value for a given key.
        """
        return self._data.get(key, default)

    @property
    def llm(self) -> Dict[str, Any]:
        return self.get('llm', {})