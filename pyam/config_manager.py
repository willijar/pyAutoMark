# Copyright 2023, Dr John A.R. Williams
# SPDX-License-Identifier: GPL-3.0-only

"""Implementation of ConfigManager Class

A Base class for loading and managing configuration files
"""

import json
from pathlib import Path
from typing import Any

class ConfigManager:
    """Base class for entities which have configuration files

    Attributes:
      domain: String representing schmea domain
      config_path: The Path to the configuration file
      manifest: The dictionary of loaded configuration parameters

    Class Attributes:
     _root: The top level global configuration
    """

    _global_config={}
    
    def __init__(self, config_path: Path, domain: str):
        self.domain: str = domain
        self.config_path: Path = config_path
        self.load()

    def load(self) -> dict:
        """Load configuration from a json file into internal manifest dictionary.

        If file doesn't exist creates a new empty dictionary

        Returns:
            manifest: Dictionary of configuration data
        """
        if self.config_path.exists():
            with open(self.config_path, "r") as fid:
                self.manifest = json.load(fid)
        else:
            self.manifest = {}
        return self.manifest

    def store(self) -> None:
        """Store manifest to configuration file, overwriting it."""
        with open(self.config_path, "w") as fid:
            fid.write(json.dumps(self.manifest, indent=2, sort_keys=True))

    def __getitem__(self, index: str) -> Any:
        """Given a configuration index returns the value or a key error

        Will accept deep indexes in '.' format e.g. assessor.username

        Will raise key error if no value found.
        """
        keys = index.split(".")
        dic = self.manifest
        for key in keys[:-1]:
            if not isinstance(dic,dict):
                break
            dic = dic[key]
        if isinstance(dic,dict):
            return dic[keys[-1]]
        raise KeyError(f"{index} not found.")


    def __setitem__(self, index: str, newvalue: Any) -> None:
        """Set a configuration item

        Will accept deep indexes in '.' format e.g. assessor.username

        Does NOT write to configuration file - call store method to do that.
        """
        keys = index.split(".")
        dic = self.manifest
        for key in keys[:-1]:
            if dic.get(key, None) is None:
                dic[key] = {}
            dic = dic[key]
        dic[keys[-1]] = newvalue

    def get(self, index: str, default: Any = []) -> Any:
        """Given a configuration index return a value

        If default is given return that if not in configurations.
        If no default is given loop it up in global config - return None if not found

        Args:
          index: An index (may be in '.' format e.g. assessor.username)
          default: Default value or CONFIG is global dictionary is to be searched as well

        Returns:
          value: The retrieved value
        """
        try:
            return self[index]
        except KeyError:
            if default is not self.get.__defaults__[0]:
                return default
            try:
                return ConfigManager._global_config[index]
            except KeyError:
                return None