# Copyright 2023, Dr John A.R. Williams
# SPDX-License-Identifier: GPL-3.0-only
"""Support functions for assessing students and running tests by cohort

Classes:
  Cohort: representing a specific cohort
  Student: representing a student in a cohort

Functions:
  get_cohort:
    Gets a cohort by name (or default cohort)
  current_academic_year:
    returns a generated default cohort name by current (UK style) academic year
"""
import subprocess
import logging
import json
import glob
import re
from typing import Union
from datetime import date, datetime
from pathlib import Path
import pyam.config as config
from pyam.config import CONFIG
from pyam.files import read_csv
from pyam.run_pytest import run_pytest


def current_academic_year() -> str:
    """Current (by date) academic year to use as a cohort name

    This is based on common UK naming where the academic year starts in late September
    and finished in June with referred assessments are in July/August

      September--December it returns the current year
      January to June return previous year
      July-August returns <previous year>-referred

    Returns:
       academic_year: The academic year
    """
    today = date.today()
    year = today.year
    if today.month < 9:
        year -= 1
        if today.month > 6:
            return f"{year}-referred"
    return str(year)


class Cohort(config.ConfigManager):
    """Class representing a cohort of students with associated tests and reports

    Inherits from:
      config.ConfigManager:
        To load configuration from manifest.json in Cohort directory and provide log handling

    Attributes:
      name: The cohort name (subdirectory name) (e.g. academic year of study)
      path: The Path to this cohort
      test_path: The Path to the tests for this cohort
      report_path: The Path to report directory for this cohort
      log: The Logger for cohort.

    Methods:
      students: Return students matching a specified name or names
      start_log_section: Starts a new named section in the cohort log
      tests: Returns the dictionary of tests for this cohort
    """

    def __init__(self, name):
        self.name: str = name
        self.path: Path = CONFIG.cohorts_path / name
        self.test_path: Path = CONFIG.tests_path / name
        self.report_path: Path = CONFIG.reports_path / name
        self.report_path.mkdir(exist_ok=True)
        super().__init__(self.path / "manifest.json", "cohort")
        self.log: logging.Logger = logging.getLogger("cohort")
        self.log.handlers.clear()
        handler = logging.FileHandler(filename=self.report_path / "info.log",
                                      mode="a")
        handler.setFormatter(
            logging.Formatter('%(asctime)s: %(levelname)-8s: %(message)s',
                              '%Y-%m-%d %H:%M:%S'))
        self.log.addHandler(handler)
        if not self.path.exists():
            raise FileNotFoundError(self.path)
        for path in (self.test_path, self.report_path):
            path.mkdir(exist_ok=True)
        student_list = []
        for rec in read_csv(self.path / "students.csv",True):
            student_list.append(Student(self, rec))
        self._students: 'tuple[Student]' = tuple(student_list)

    def students(self, name: 'Union[str, None, list[str]]' = None
                ) -> 'Union[Student, list[Student]]':
        """Return student or students from a cohort.

        Finds students by full name, student id or username in cohort.

        Args:
          name:
            Name or names to be found in the cohort. May be username, student_id or common name

        Returns:
          If name is not given prodes list of all students in cohort
          If name is a string returns the first matching student found
          If name is a list return list of students corresponding to list of names
        """
        if not name:
            return list(self._students)
        if isinstance(name, str):
            for student in self._students:
                if name in (student.username, student.student_id,
                            student.name()):
                    return student
            raise KeyError(f"Student {name} not found in {self.name} cohort.")
        students = []
        for i in name:
            students.append(self.students(i))
        return students

    def start_log_section(self, title: str) -> None:
        "Write a section header in cohort log file"
        fix = "=" * (40 - len(title) // 2)
        self.log.info("%s %s %s", fix, title, fix)

    def tests(self) -> dict:
        """Return dictionary of tests for this cohort indexed by pytest nodeids

        If a manifest.json is provided in the test directory then this is the "tests"
        value from that file. Otherwise the nodeids are collected by pytest and the values
        fields are empty dictionaies. Future implementations may use the values.
        """
        test_manifest_path = self.test_path / "manifest.json"
        test_manifest = None
        if test_manifest_path.exists():
            with open(test_manifest_path, "r") as fid:
                test_manifest = json.load(fid).get("tests", None)
        if not test_manifest:
            result = run_pytest(self, '--collect-only', '-q')
            test_manifest = {}
            for line in result.stdout.splitlines():
                if len(line) == 0:
                    break
                if line.startswith(self.name + "/"):
                    line = line[len(self.name) + 1:]
                test_manifest[line] = {}
        return test_manifest


class Student:
    """A student in a cohort. Initialised from students.csv file in cohort

    Attributes:
      username: Their username
      path: The Path to where the students submission resides.
      student_id: Their official student id
      last_name: Their family name
      first_name: their first name
      cohort: The Cohort in which they reside
      course: Possible subcohort course name
      github_username: Github username if specified
    """

    def __init__(self, cohort: Cohort, rec: dict):
        """Initialise student into cohort from a csv record rec

        Args:
          cohort: The Cohort object to which this student belongs
          rec: A dictionary of values from csv file to initialise student from
        """
        self.rec = rec
        self.cohort = cohort
        self.username = rec["Username"]
        self.student_id = rec["Student ID"]
        self.last_name = rec["Last Name"]
        self.first_name = rec["First Name"]
        self.course = rec.get("Child Course ID", self.cohort.get("course"))
        self.github_username = rec.get("Github Username", None)
        folder = cohort.get("student-folder-name")
        if folder:
            folder = self.rec[folder]
        else:
            folder = self.username
        self.path = self.cohort.path / folder

    def __hash__(self):
        return hash((self.cohort.name, self.username))

    def __repr__(self):
        return f"<Student {self.cohort.name}/{self.student_id}>"

    def __str__(self):
        return self.name()

    def name(self, style: str = "ref") -> str:
        """Return common name formats - default is student id first name, last name

        Args:
          style: Style - can be a field from csv file, username or ref(default)

        Returns:
          name string in given style. Default is ref - student username, Lastname and firstname
        """
        if style:
            if style in self.rec:
                return self.rec[style]
            if style == "ref":
                return f"{self.student_id} ({self.last_name}, {self.first_name})"
            if style == "username":
                return f"{self.username} ({self.last_name}, {self.first_name})"
        return f"{self.last_name}, {self.first_name}"

    def check_manifest(self,
                       files: Union[list, None] = None,
                       log: bool = False):
        """Check if student directory contains all files on cohort manifest

        Args:
          files: (optional) List of files to find. If not given use cohort manifest
          log (bool): If True log missing files in cohort logger

        Returns:
          List of missing files
        """
        if not files:
            files = self.cohort.get("files", ())
        if not self.path.exists():
            self.cohort.log.warning("No submission: %s",self.name())
            return files.keys()
        missing = []
        for rec in files.keys():
            if not (self.path / rec).exists():
                missing.append(rec)
        if missing and log:
            self.cohort.log.warning("Missing Files: %-40s: %2d missing: %s",
                                    self.name(), len(missing), missing)
        return missing

    def repository_name(self):
        """Github repository name if applicable else False"""
        if self.github_username:
            github = self.cohort.get("github.template", None)
            if github:
                return f"{github}-{self.github_username}"
        return False

    def repository_url(self):
        """Return students github repository url if present else False"""
        name = self.repository_name()
        if name:
            return f"{self.cohort['github.url']}/{self.repository_name()}"
        return False

    def github_retrieve(self):
        """Clone or pull asssessments for this student from their repository."""
        if self.path.exists():
            action = ["git", "pull"]
            cwd = self.path
        elif not self.repository_url():
            self.cohort.log.warning(f"No repository known for '{self.name()}'")
            return False
        else:
            action = ["git", "clone", self.repository_url(), self.path]
            cwd = self.cohort.path
        # pylint: disable=W1510
        proc = subprocess.run(action,
                              cwd=str(cwd),
                              capture_output=True,
                              text=True)
        if proc.returncode == 0:  # successful
            self.cohort.log.info(
                f"Successful {action[:2]} {self.repository_name()}"\
                 + f" to '{self.path.relative_to(self.cohort.path)}'"\
                 + f" for '{self.name()}': {proc.stdout.strip()}"
            )
            return True
        self.cohort.log.error(
            f"Unable to {action[:2]} {self.repository_name()}"\
            + f" to '{self.path.relative_to(self.cohort.path)}'"\
            +f" for '{self.name()}: {proc.stdout} {proc.stderr}"
        )
        return False

    def github_lastcommit(self) -> Union[datetime, None]:
        "Return last github commit time or None"
        if self.path.exists():
            result = subprocess.run(("git", "log", "-1", r"--format=%cd"),
                                    cwd=self.path,
                                    capture_output=True,
                                    text=True,
                                    check=True)
            if result.returncode == 0:
                return datetime.strptime(result.stdout,
                                         "%a %b %d %H:%M:%S %Y %z\n")
            raise ValueError(result.stderr)
        return None

    def find_files(self,
                   pathname: str,
                   containing: str = None,
                   recursive: bool = False) -> list:
        """Return filtered list of files found in student directory.

        If containing is given also filter to files containing this regexp
        If recursive is true also recurse subdirectories looking for matches

        Args:
          pathname: Unix style pathaname glob
          containing: An optional regexp to match against file contents
          recursive: If true also look in subdirectories

        Returns:
          List of files found - may be empty list
        """
        files = glob.glob(str(self.path) + "/" + pathname, recursive=recursive)
        if not containing:
            return files
        matching = []
        matcher = re.compile(containing)
        for file in files:
            with open(file, 'r') as fid:
                if matcher.findall(fid.read()):
                    matching.append(file)
        return matching


def get_cohort(name: str = CONFIG.get("cohort",
                                      current_academic_year())) -> Cohort:
    """Return cohort for given name or current defaultcohort if name=None

    Args:
      name:
        Optional name of cohort to load.
        If not present will use default - "cohort" field from configuration
        Or use calculated current_academic_year
    """
    assert name is not None or CONFIG.cohort
    if (not (CONFIG.cohort) or CONFIG.cohort.name != name):
        CONFIG.cohort = Cohort(name)
    return CONFIG.cohort


def list_cohorts():
    """Returns a list of valid cohorts

    Subdirectories of cohorts which have student.csv and manifest.json files
    """
    results = []
    for path in CONFIG.cohorts_path.iterdir():
        if path.is_dir():
            if (path / "manifest.json").exists() and (path /
                                                      "students.csv").exists():
                results.append(str(path.stem))
    return results
