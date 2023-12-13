# Copyright 2023, Dr John A.R. Williams
# SPDX-License-Identifier: GPL-3.0-only
"""Classes to provide access to cohort and student information.

Classes

  :class:`Cohort`
    representing a specific cohort
  :class:`Student`
    representing a student in a cohort

Functions

  :func:`get_cohort`
    Gets a cohort by name (or default cohort)
  :func:`current_academic_year`
    returns a generated default cohort name by current (UK style) academic year

"""
import subprocess
import logging
import json
import shutil
import hashlib
import re
import glob
from os import walk
from typing import Union, Dict, List
from datetime import date, datetime
from pathlib import Path
import pyam.config_manager as config
from pyam.config import CONFIG
from pyam.files import read_csv
from pyam.run_pytest import run_pytest


def current_academic_year() -> str:
    """Current (by date) academic year to use as a cohort name

    This is based on common UK naming where the academic year starts in late September
    and finished in June with referred assessments are in July/August

    Returns:
        September--December
          returns the current year
        January--June
          return previous year
        July-August
          returns <previous year>-referred

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

    Attributes:
      name (str): The cohort name (subdirectory name) (e.g. academic year of study)
      path (Path): The Path to this cohort
      test_path (Path): The Path to the tests for this cohort
      report_path (Path) : The Path to report directory for this cohort
      log (logging.Logger): The Logger for cohort.
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
        for rec in read_csv(self.path / "students.csv",
                            self.student_columns()):
            student_list.append(Student(self, rec))
        self._students: 'tuple[Student]' = tuple(student_list)

    def student_columns(self) -> List[tuple]:
        """Return a list of student column information for this cohort configuration

        Returns:
            A list of tuples of regex and column titles suitable for read_csv
        """
        cols = []
        for name, value in config.SCHEMA["student-column"].items():
            regex = self.get(f"student-column.{name}",
                             value.get("default", name))
            cols.append((regex, name))
        return cols

    def students(self,
                 name: Union[str, None, List[str]] = None
                ) -> 'Union[Student, List[Student]]':
        """Return student or students from a cohort.

        Finds students by full name, student id or username in cohort.

        Args:
          name: Name or names to be found in the cohort.
            May be *username*, *student_id* or *common name*

        Returns:
          If name is not given prodes list of all students in cohort.

          If name is a string returns the first matching student found.

          If name is a list return list of students corresponding to list of names.
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

    def tests(self) -> Dict[str, Dict]:
        """Return dictionary of tests for this cohort indexed by pytest nodeids

        If a manifest.json is provided in the test directory then this is the "tests"
        value from that file. Otherwise the nodeids are collected by pytest and the values
        fields are empty dictionaies. Future implementations may use the values.

        Returns:
          A dictionary of tests for this cohort indexed by pytest nodeids.
          Value is a dictionary of test attributes from the test manifest if provided.
          Currently "description" is used to provide a human readable description
          and "mark" to provide a numerical mark for this test in the generated template.
        """
        #Load manifest data if present
        test_manifest_path = self.test_path / "manifest.json"
        test_manifest = {}
        if test_manifest_path.exists():
            with open(test_manifest_path, "r") as fid:
                test_manifest = json.load(fid).get("tests", None)
        #Ensure all tests are included by collecting from pytest
        result = run_pytest(self, '--collect-only', '-q')
        for line in result.stdout.splitlines():
            if len(line) == 0:
                break
            if line.startswith(self.name + "/"):
                line = line[len(self.name) + 1:]
            if not test_manifest.get(line):
                test_manifest[line] = {}
        return test_manifest


class Student:
    """A student in a cohort. Initialised from students.csv file in cohort

    Attributes:
      username (str): Their username
      path (Path): The Path to where the students submission resides.
      student_id (str): Their official student id
      last_name (str): Their family name
      first_name (str): their first name
      cohort (Cohort): The Cohort in which they reside
      course (str): Possible subcohort course name
      github_username (str): Github username if specified
    """

    def __init__(self, cohort: Cohort, rec: dict):
        """Initialise student into cohort from a csv record rec

        Args:
          cohort: The Cohort object to which this student belongs
          rec: A dictionary of values from csv file to initialise student from
        """
        self.rec = rec
        self.cohort = cohort
        self.username = rec["username"]
        self.student_id = rec["studentid"]
        self.last_name = rec["lastname"]
        self.first_name = rec["firstname"]
        self.course = rec.get("course", self.cohort.get("course"))
        self.github_username = rec.get("github-username", None)
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

    def __lt__(self,other):
        return (self.last_name, self.first_name) < (other.last_name, other.first_name) 
    
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
                       log: bool = False) -> List[str]:
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
            self.cohort.log.warning("No submission: %s", self.name())
            return files.keys()
        missing = []
        if log:
            log=self.cohort.log
        for rec in files.keys():
            if not self.file(rec,False):
                missing.append(rec)
        if missing and log:
            self.cohort.log.warning("Missing Files: %s - %s",
                                    self.name(), missing)
        return missing

    def repository_name(self) -> Union[str, None]:
        """Return Github repository name if applicable else False
        """
        if self.github_username:
            github = self.cohort.get("github.template", None)
            if github:
                return f"{github}-{self.github_username}"
        return None

    def repository_url(self) -> Union[str, None]:
        """Return students github repository url if present else False"""
        name = self.repository_name()
        if name:
            return f"{self.cohort['github.url']}/{self.repository_name()}"
        return None
    
    def git(self,*args,**kwargs):
        """Run git with given args in the student repository. 

        Return stdout if successful.
        if log keyword is set Logs action either as info or as an error depending on success
        """
        log=kwargs.get("log",True)
        cwd= kwargs.get("cwd",self.path)
        try:
            # pylint: disable=W1510
            proc=subprocess.run(("git",*args), cwd=cwd, text=True, check=True, capture_output=True)
            if log:
                self.cohort.log.info(
                f"Successful {args} {self.repository_name()}"\
                 + f" for '{self.name()}': {proc.stdout.strip()}"
                )
            return proc.stdout.strip()
        except subprocess.CalledProcessError as error:
            if log:
                self.cohort.log.error(
                    f"Unable to {args} {self.repository_name()}"\
                    + f" to '{self.path.relative_to(self.cohort.path)}'"\
                    +f" for '{self.name()}: {error.output.strip()} {error.stderr.strip()}"
                )
            return False


    def github_retrieve(self,reset: bool=True,branch=None) -> bool:
        """Clone or pull assessments for this student from their repository.

        Returns:
          Success of retrieval
        """
        if not self.repository_url():
            self.cohort.log.warning(f"No repository known for '{self.name()}'")
            return False
        if self.path.exists():
            if reset: # by default do a reset hard first to ensure work area is clean
                self.git("reset","--hard",log=False)
                if branch:
                    self.git("checkout",branch)
            return self.git("pull")
        else:
            return self.git("clone", self.repository_url(), self.path, cwd=self.cohort.path)

    def github_push(self, files: List[Path], subdir=None, reset: bool=True, branch: str=None, msg: str = "Push from pyAutoMark"):
        """Push given set of files into student repository

        Args:
          files: List of files or directories to copy
          subdir: If set - the name of subdirectory in student repository to copy files into
          reset: If True, do a github_retrieve first to ensure we are consistent with student repo
          branch: If set checkout and push files into this branch

        If branch is specified original branch checkou in local repository is restored after push
        """
        if reset:
            #rensure we are synced with student work if reset is true
            self.github_retrieve(reset=True)
        if branch:
            #save current branch name and checkout specified branch
            original_branch = self.git("branch", "--show-current",log=False)
            self.git("checkout", branch,log=False)
        destination = self.path
        if subdir:
            destination = destination / subdir
            if not destination.exists():
                destination.mkdir(parents=True, exist_ok=True)
        for file in files:
            if file.is_file():
                shutil.copyfile(file,destination/file.name)
            elif file.is_dir():
                shutil.copytree(file,destination/file.name,copy_function=shutil.copyfile,dirs_exist_ok=True)
        self.git("add","--all",log=False)
        self.git("commit","-m", msg,log=False)
        self.git("push")
        if branch:
            self.git("checkout", original_branch,log=False)


    def checkout(self,until,branch=None):
        """Checkout last repository for student before given date until or to a specified branch"""
        if self.path.exists():
            if branch:
                self.git("checkout",branch)
            if until:
                result=self.git("log", r"--pretty='%h%'","-1", r"--format=%h","--until", until.isoformat(),log=False)
                if result:
                    self.git("checkout",result)

    def github_lastcommit(self) -> Union[datetime, None]:
        "Return last github commit time if applicable"
        if self.path.exists():
            result=self.git("log", "-1", r"--format=%cd",log=False)
            if result:
                return datetime.strptime(result,"%a %b %d %H:%M:%S %Y %z") 

    def hash(self) -> int:
        """Return a hash based on students username - this will be first integer of first 8 characters of md5hash of username"""
        return int("0x"+hashlib.md5(self.username.encode("utf-8")).hexdigest()[:8],16)

    def file(self, pattern: str, log: Union[logging.Logger,None] = None) -> Union[Path,None]:
        """Attempt to find file matching given pathname pattern based on the configuration setting
        filematch.pattern.

        Args:
            pattern: The file pattern to search for - either an exact path, glob or regexp
                depending on the configuration setting filematch.pattern
            log: If given use to log if no file found or multiple files found

        Returns:
            The path to the (first) matching file found or None if none found
        """
        matchtype=self.cohort.get("filematch.pattern")
        files=[]
        if matchtype=="exact":
            path=self.path / pattern
            if path.exists():
                files.append(path)
        elif matchtype=="glob":
            files=list(self.path.glob(pattern))
        elif matchtype=="regexp":
            matcher = re.compile(pattern)
            for path in self.path.glob("**/*"):
                if matcher.search(str(path)):
                    files.append(path)
        else:
            raise ValueError("Invalid filematch.pattern", matchtype)
        if not files:
            if log:
                log.warning("File Not Found: %s: '%s'",self.name(), pattern)
            return None
        if len(files)>1 and log:
            log.warning("Multiple files found: %s matching '%s': using %s",
                self.name(), pattern,  files[0].relative_to(self.path))
        return files[0]


    def find_files(self,
                   pathname: str,
                   containing: str = None,
                   recursive: bool = False) -> List[Path]:
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
    """Return cohort for given name or current default cohort if name=None

    Args:
      name:
        Optional name of cohort to load.
        If not present will use default - "cohort" field from configuration
        Or use calculated current_academic_year

    Returns:
       The cohort object
    """
    assert name is not None or CONFIG.cohort
    if (not (CONFIG.cohort) or CONFIG.cohort.name != name):
        CONFIG.cohort = Cohort(name)
    return CONFIG.cohort


def list_cohorts() -> List[str]:
    """List the cohorts

    These are ubdirectories of cohorts which have student.csv and manifest.json files

    Returns:
       List of valid cohort names
    """
    results = []
    for path in CONFIG.cohorts_path.iterdir():
        if path.is_dir():
            if (path / "manifest.json").exists() and (path /
                                                      "students.csv").exists():
                results.append(str(path.stem))
    return results
