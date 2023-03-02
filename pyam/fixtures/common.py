# Copyright 2023, Dr John A.R. Williams
# SPDX-License-Identifier: GPL-3.0-only
"""
Common fixtures for pyam to provide cohort and student information

Defines fixtures:
    cohort: the cohort under test
    student: the stundet being tested
    compiler: the C compiler begin used
    build_path: directory for temporary build files
    test_path: The path where the tests are kept
"""
from pathlib import Path
from typing import Union
import pytest
from pyam.config import CONFIG
from pyam.cohort import get_cohort


def pytest_addoption(parser):
    """Add in pyAutoTest control options for pytest"""
    parser.addoption("--cohort", action="store", default=None)
    parser.addoption("--student", action="store", default="solution")


def pytest_configure(config):
    """Add in pyAutoTest markers for pytest"""
    config.addinivalue_line("markers", "slow: mark test as slow")
    config.addinivalue_line("markers", "timeout: set timeout for a test.")
    
# pylint: disable=W0621
@pytest.fixture
def cohort(request):
    "The cohort where student is to be found - specified using --cohort option"
    name = request.config.getoption("--cohort")
    if name:
        return get_cohort(name)
    return get_cohort()


@pytest.fixture
def student(request, cohort):
    "The current student under test - specified using --student option"
    name = request.config.getoption("--student")
    return cohort.students(name)


@pytest.fixture
def compiler(request):
    "The C Compiler to use"
    return "gcc"


@pytest.fixture
def build_path():
    "Directory path for out of source build (executables, libs and object files)"
    return CONFIG.build_path


@pytest.fixture
def test_path(cohort):
    "Directory path containing test files"
    return cohort.test_path

@pytest.fixture
def student_files(student):
    """Fixture is function to find files for student

    Args:
      pathname: Unix style pathaname glob (or list of same)
      containing: An optional regexp to match against file contents
      recursive: If true also look in subdirectories

    Returns:
      Path(s): File Path or list of File Paths found.
        If multiple then first found will be given (or list)

    Raises:
      FileNotFoundError: if no matching file found"""
    def __student_files(
            pathnames: 'Union[str, list[str]]',
            containing: str = None,
            recursive: bool = False,
            warn_if_multiple: bool = True) -> 'Union[Path, list[Path]]':
        if isinstance(pathnames, str):
            files = student.find_files(pathnames, containing, recursive)
            if not files:
                raise FileNotFoundError(f"No file contains {containing}")
            if len(files) > 1 and warn_if_multiple:
                student.cohort.log.warning(
                    "Multiple files matching '%s' - selected %s.", containing,
                    files[0])
            return files[0]
        files = []
        for pathname in pathnames:
            files.append(__student_files(pathname, containing, recursive, warn_if_multiple))
        return files

    return __student_files


# @pytest.fixture(autouse=True)
# def run_before_and_after_tests(build_dir,request):
#     """Fixture to execute asserts before and after a test is run"""
#     build_dir.mkdir(exist_ok=True) # ensure build directory exists
#     yield # Run test
#     #TearDown
#     testname = request.node.name
#     #outcome=request.node.result_call.outcome
#    # print("Test:",testname,"--",outcome)