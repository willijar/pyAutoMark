# Copyright 2023, Dr John A.R. Williams
# SPDX-License-Identifier: GPL-3.0-only
"""Top level configuration for the assessment marking scripts"""
from pathlib import Path
import logging
import json
import argparse

_HERE = Path(__file__).resolve().parent

# Gobal configuration
# pylint: disable=C0103
CONFIG = None


class ConfigManager:
    """Base class for entities which have configuration files"""
    domain: str
    config_path: Path
    config: dict = {}

    def __init__(self, config_path, domain):
        self.domain = domain
        self.config_path = config_path
        self.load()

    def load(self):
        """Load configuration from a json file into internal manifest dictionary.
        If file doesn't exist creates a new dictionary

        Returns:
            manifest: The dictionary of values from the configuration file
        """
        if self.config_path.exists():
            with open(self.config_path, "r") as fid:
                self.manifest = json.load(fid)
        else:
            self.manifest = {}
        return self.manifest

    def store(self):
        """Store manifest to configuration file, overwriting it."""
        with open(self.config_path, "w") as fid:
            fid.write(json.dumps(self.manifest, indent=2, sort_keys=True))

    def __getitem__(self, index):
        """Given a configuration index returns the value or a key error"""
        keys = index.split(".")
        dic = self.manifest
        for key in keys[:-1]:
            dic = dic[key]
        return dic[keys[-1]]

    def __setitem__(self, index, newvalue):
        keys = index.split(".")
        dic = self.manifest
        for key in keys[:-1]:
            if dic.get(key, None) is None:
                dic[key] = {}
            dic = dic[key]
        dic[keys[-1]] = newvalue

    def get(self, index, default=CONFIG):
        """Given a configuration index return a value
        If default is given return that if not in configurations.
        If no default is given loop it up in global config - return None if not found"""
        try:
            return self[index]
        except KeyError:
            if default != CONFIG:
                return default
            try:
                return CONFIG[index]
            except KeyError:
                return None


class Config(ConfigManager):
    """Global (root) configuration"""
    root_path: Path
    tests_path: Path
    cohorts_path: Path
    build_path: Path
    reports_path: Path
    log: logging.Logger

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
        self.root_path = self.get("root_path", _HERE.parent)
        self.tests_path = self.get("test_path", _HERE)
        self.cohorts_path = self.get("cohort_path", self.root_path / "cohorts")
        self.build_path = self.get("build_path", self.root_path / "build")
        self.reports_path = self.get("report_path", self.root_path / "reports")
        for path in (self.cohorts_path, self.tests_path, self.build_path,
                     self.reports_path):
            path.mkdir(exist_ok=True)
        self.error_log = logging.FileHandler(filename=self.build_path /
                                             "error.log",
                                             mode='a')
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

        self.log = logging.getLogger()
        self.log.addHandler(self.error_log)
        self.log.addHandler(self.console_log)
        logging.getLogger("cohort").setLevel(logging.INFO)
        self.cohort = None


CONFIG = Config()


def add_args(parser=argparse.ArgumentParser(description=__doc__)):
    """Return Parsed arguments for find-duplicates"""
    parser.add_argument('key', help="Key of value to be set")
    parser.add_argument('value',
                        help='value to be set',
                        nargs='?',
                        default=None)
    parser.add_argument('--type',
                        help="Type conversion to perform e.g. int or float")


def main(args=None):
    """Main program - set configuration using command line arguments"""
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
