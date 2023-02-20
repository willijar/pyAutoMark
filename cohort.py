# Copyright 2023, Dr John A.R. Williams
# SPDX-License-Identifier: GPL-3.0-only
"""Support functions for assessing students and running tests by cohort
 reads student details from CSV file, checks manifest etc
 Only one cohort can be active at once - use getCohort(name) to get/set root level cohort"""
import subprocess
import logging
import json
from datetime import date
from pathlib import Path
import config
from config import CONFIG
from files import read_csv


def get_cohort(name=CONFIG.get("cohort", None)):
    """Return cohort for given name or current cohort if name=None"""
    assert name is not None or CONFIG.cohort
    if (not (CONFIG.cohort) or CONFIG.cohort.name != name):
        CONFIG.cohort = Cohort(name)
    return CONFIG.cohort


def current_cohort_name():
    """Return current (by date) cohort name"""
    today = date.today()
    year = today.year
    if today.month < 9:
        year -= 1
        if today.month > 6:
            return f"{year}-referred"
    return str(year)


class Cohort(config.ConfigManager):
    """Class representing a cohort of students"""
    name: str  # cohort name (academic year)
    practical: str  # practical name (on github classroom)
    students: tuple  # list of students in this cohort
    path: Path  # Path to this cohort
    test_path: Path
    test_manifest: dict

    def __init__(self, name):
        self.name = name
        student_list = []
        self.path = CONFIG.cohorts_path / name
        self.test_path = CONFIG.tests_path / name
        self.report_path = CONFIG.reports_path / name
        self.report_path.mkdir(exist_ok=True)
        super().__init__(self.path / "manifest.json", "cohort")
        self.log = logging.getLogger("cohort")
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
        for rec in read_csv(self.path / "students.csv", columns=True):
            student_list.append(Student(self, rec))
        self.students = tuple(student_list)

    def student(self, name):
        """Find student by full name, student id or username in cohort.
        If an iterable type is given return list of students"""
        if not name:
            return tuple(self.students)
        if isinstance(name, str):
            for student in self.students:
                if name in (student.username, student.student_id,
                            student.name()):
                    return student
            raise KeyError(f"Student {name} not found in {self.name} cohort.")
        students = []
        for i in name:
            students.append(self.student(i))
        return students

    def start_log_section(self, title):
        "Write a section header in cohort log file"
        fix = "=" * (40 - len(title) // 2)
        self.log.info("%s %s %s", fix, title, fix)

    # def import_py(self, module_name):
    #     spec = importlib.util.spec_from_file_location(
    #         module_name, self.path(module_name + ".py"))
    #     module = importlib.util.module_from_spec(spec)
    #     spec.loader.exec_module(module)

    def tests(self):
        """Return hash of tests to be considered - dictionary by nodeids
        - either from test manifest or from pytest cache"""
        test_manifest_path = self.test_path / "manifest.json"
        self.test_manifest = None
        if test_manifest_path.exists():
            with open(self.path / "manifest.json", "r") as fid:
                self.test_manifest = json.load(fid).get(
                    "tests", self.test_manifest)
        if not self.test_manifest:
            result = subprocess.run(
                ["pytest", '--collect-only', '-q', '--cohort', self.name],
                cwd=self.test_path,
                text=True,
                capture_output=True,
                check=True)
            self.test_manifest = {}
            for line in result.stdout.splitlines():
                if len(line) == 0:
                    break
                self.test_manifest[line] = {}
        return self.test_manifest


class Student:
    """Class representing student work"""
    username: str  # Blackboard username
    student_id: str  # Aston student id
    last_name: str
    first_name: str
    rec: dict
    cohort: Cohort  # Cohort to which this student belongs
    course: str = None  #child course id from blackboard (if set)
    github_username: str = None  #github username if specified
    path: Path = None

    def __init__(self, cohort: Cohort, rec: dict):
        """Initialise from a csv record"""
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
        "Hash by username"
        return self.username.__hash__()

    def __str__(self):
        return f"<Student {self.cohort.name}/{self.name()}>"

    def name(self, style="ref"):
        "Return common name formats"
        if style:
            if style in self.rec:
                return self.rec[style]
            if style == "ref":
                return f"{self.student_id} ({self.last_name}, {self.first_name})"
            if style == "username":
                return f"{self.username} ({self.last_name}, {self.first_name})"
        return f"{self.last_name}, {self.first_name}"

    def check_manifest(self, files=None, log=False):
        "Check if student directory contains all files on cohort manifest"
        if not files:
            files = self.cohort.get("files", ())
        missing = []
        for rec in files.keys():
            if not (self.path / rec).exists():
                missing.append(rec)
        if missing and log:
            self.cohort.log.warning(
                f'{self.student_id} "{self.name()}" missing files: {missing}')
        return missing

    def repository_name(self):
        """Github repository name if applicable else None"""
        if self.github_username:
            github = self.cohort.get("github", None)
            if github:
                return f"{github['practical']}-{self.github_username}"
        return False

    def repository_url(self):
        """Return students github repository url"""
        name = self.repository_name()
        if name:
            return f"{self.cohort['github.url']}/{self.repository_name()}"
        return False

    def github_retrieve(self):
        """Clone or pull asssessments for each student in studentlist"""
        if self.path.exists():
            action = ["git", "pull"]
            cwd = self.path
        elif not self.repository_url():
            self.cohort.log.warning(f"No repository known for '{self.name()}'")
            return False
        else:
            action = ["git", "clone", self.repository_url(), self.path]
            cwd = self.cohort.path
        proc = subprocess.run(action,
                              cwd=str(cwd),
                              capture_output=True,
                              text=True,
                              check=True)
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


# pylint: disable=W0613
def main(args=None):
    """Main routine - checks student manifest in a cohort"""
    cohort = get_cohort(current_cohort_name())
    for student in cohort.students:
        missing = student.check_manifest(cohort.get("Files", None), log=False)
        if missing:
            print(f'"{student.name()}" missing {missing}')


def add_args(parser):
    """Add args for this command - none"""


if __name__ == "__main__":
    main()
