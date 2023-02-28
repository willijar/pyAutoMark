# Copyright 2023, Dr John A.R. Williams
# SPDX-License-Identifier: GPL-3.0-only
"""Top level configuration handling for the assessment marking scripts

Attributes:
  CONFIG: A ConfigManager with the global configuration data
"""

import pathlib
from pathlib import Path
import logging
from pyam.config_manager import ConfigManager

CONFIG = None

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
        global CONFIG
        assert not CONFIG
        # find a configuration path up to home directory
        self.root_path = current_dir
        while not (self.root_path / "pyAutoMark.json").exists():
            if self.root_path == self.root_path.home():
                raise FileNotFoundError("pyAutoMark.json")
            self.root_path = self.root_path.parent
        super().__init__(self.root_path / "pyAutoMark.json", "global")
        self.tests_path: Path = self.get("path.tests", self.root_path / "tests")
        self.cohorts_path: Path = self.get("path.cohorts", self.root_path / "cohorts")
        self.build_path: Path = self.get("path.build", self.root_path / "build")
        self.reports_path: Path = self.get("path.reports", self.root_path / "reports")
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

        CONFIG = self
        ConfigManager._global_config = self

_Config()
