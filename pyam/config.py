# Copyright 2023, Dr John A.R. Williams
# SPDX-License-Identifier: GPL-3.0-only
"""Top level configuration handling for the assessment marking scripts

Attributes:
  CONFIG: A ConfigManager with the global configuration data

Classes:
  ConfigManager: Base class for loading and managing configuration files
"""

import pathlib
from pathlib import Path
import logging
import json
from typing import Any

# Gobal configuration
CONFIG = None


class ConfigManager:
    """Base class for entities which have configuration files

    Attributes:
      domain: String representing schmea domain
      config_path: The Path to the configuration file
      manifest: The dictionary of loaded configuration parameters
    """

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
            dic = dic[key]
        return dic[keys[-1]]

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
                return CONFIG[index]
            except KeyError:
                return None


class _Config(ConfigManager):
    """Global (root) configuration

    Attributes:
      root_path: top level Root path for assessments etc
      test_paths: Path to tests
      cohort_path: Path to cohorts
      build_path: Path for out of source build
      reports_path: Path for generated reports
      log: global Logger
      cohort: The current cohort being processed
    """

    def __init__(self, current_dir=pathlib.Path.cwd()):
        # find a configuration path up to home directory
        self.root_path = current_dir
        while not (self.root_path / "pyAutoMark.json").exists():
            if self.root_path == self.root_path.home():
                raise FileNotFoundError("pyAutoMark.json")
            self.root_path=self.root_path.parent
        super().__init__(self.root_path / "pyAutoMark.json", "global")
        self.root_path: Path = self.get("root_path", self.root_path)
        self.tests_path: Path = self.get("test_path", self.root_path / "tests")
        self.cohorts_path: Path = self.get(
            "cohort_path", self.root_path / "cohorts")
        self.build_path: Path = self.get(
            "build_path",  self.root_path / "build")
        self.reports_path: Path = self.get(
            "report_path", self.root_path / "reports")
        for path in (self.cohorts_path, self.tests_path, self.build_path,
                     self.reports_path):
            path.mkdir(exist_ok=True)
        self.error_log: logging.Logger = logging.FileHandler(
            filename=self.build_path / "error.log", mode='a')
        self.error_log.setLevel(logging.ERROR)
        self.error_log.setFormatter(
            logging.Formatter(
                '%(asctime)-12s: %(name)8s: %(levelname)8s: %(message)s',
                '%Y-%m-%d %H:%M:%S'))
        ## warning and above go to console - no need for time in format, log warning messages
        self.console_log = logging.StreamHandler()
        self.console_log.setLevel(level=logging.WARN)
        self.console_log.setFormatter(
            logging.Formatter('%(levelname)8s %(message)s'))

        self.log: logging.Logger = logging.getLogger()
        self.log.handlers.clear()
        self.log.addHandler(self.error_log)
        self.log.addHandler(self.console_log)
        logging.getLogger("cohort").setLevel(logging.INFO)
        self.cohort = None

CONFIG = _Config()
