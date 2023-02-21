# Copyright 2023, Dr John A.R. Williams
# SPDX-License-Identifier: GPL-3.0-only
"""Top level configuration handling for the assessment marking scripts

Attributes:
  CONFIG: A ConfigManager with the global configuration data

Classes:
  ConfigManager: Base class for loading and managing configuration files
"""

from pathlib import Path
import logging
import json
import argparse
from typing import Any

_HERE = Path(__file__).resolve().parent

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

    def get(self, index: str, default: Any = CONFIG) -> Any:
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
            if default != CONFIG:
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

    def __init__(self):
        # find a configuration path up to home directory
        path = _HERE
        while not (path / "pyAutoMark.json").exists():
            if path == path.home():
                path = _HERE
                break
            path = path.parent
        path = path / "pyAutoMark.json"
        super().__init__(path, "global")
        self.root_path: Path = self.get("root_path", _HERE.parent)
        self.tests_path: Path = self.get("test_path", _HERE)
        self.cohorts_path: Path = self.get("cohort_path",
                                           self.root_path / "cohorts")
        self.build_path: Path = self.get("build_path",
                                         self.root_path / "build")
        self.reports_path: Path = self.get("report_path",
                                           self.root_path / "reports")
        for path in (self.cohorts_path, self.tests_path, self.build_path,
                     self.reports_path):
            path.mkdir(exist_ok=True)
        self.error_log: logging.Logger = logging.FileHandler(
            filename=self.build_path / "error.log", mode='a')
        self.error_log.setLevel(logging.ERROR)
        self.error_log.setFormatter(
            logging.Formatter(
                '%(asctime)-12s: %(name)-8s: %(levelname)-8s: %(message)s',
                '%Y-%m-%d %H:%M:%S'))
        ## warning and above go to console - no need for time in format, log warning messages
        self.console_log = logging.StreamHandler()
        self.console_log.setLevel(level=logging.WARN)
        self.console_log.setFormatter(
            logging.Formatter('%(name)-8s: %(levelname)-8s %(message)s'))

        self.log: logging.Logger = logging.getLogger()
        self.log.addHandler(self.error_log)
        self.log.addHandler(self.console_log)
        logging.getLogger("cohort").setLevel(logging.INFO)
        self.cohort = None


CONFIG = _Config()


def add_args(parser: argparse.ArgumentParser = argparse.ArgumentParser(description=__doc__)) -> None:
    """Add arguments for config command"""
    parser.add_argument('key', help="Key of value to be set in '.' format e.g. assessor.username")
    parser.add_argument('value',
                        help='value to be set (if no value give output current value)',
                        nargs='?',
                        default=None)
    parser.add_argument('--type',
                        help="Type conversion to perform on value e.g. int,float")


def main(args: argparse.Namespace = None) -> None:
    """Set configuration parameters.

    Keys may be in '.' format e.g. 2022.assessor.username sets assessor.username in cohort 2022
    global name may be used to set global parameters across all cohorts (unless set locally).
    If no value is given print out current value."""
    if args is None:
        parser = argparse.ArgumentParser(description=__doc__)
        add_args(parser)
        args = parser.parse_args()
    components = args.key.split('.')
    domain = components[0]
    remainder = ".".join(components[1:])
    if domain == 'global':
        conf = CONFIG
    else:
        path = CONFIG.cohorts_path / domain
        if not path.exists():
            raise KeyError(f"Configuration Path {domain}")
        conf = ConfigManager(path / "manifest.json", "cohort")
    if args.value is not None:
        conf[remainder] = args.value
        conf.store()
        if conf == CONFIG and conf.config_path.parent != _HERE:
            conf.log.warning(
                "Writing to global configuration file %s:%s at %s", args.key,
                args.value, conf.config_path)
    else:
        print(conf[remainder])


if __name__ == "__main__":
    main()
