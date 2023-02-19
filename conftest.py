# Copyright 2023, Dr John A.R. Williams
# SPDX-License-Identifier: GPL-3.0-only
"""pytest configuration options

Defines the following command line options:
    --cohort: Name of cohort to be processed
    --student: Name of student to be tested
    --c-compiler: Name of C compiler to use

Loads in pytest plugins:
    vhdl_test: For testing VHDL code
    mock_test: for testing embedded C using mocking

Defines fixtures:
    cohort: the cohort under test
    student: the stundet being tested
    compiler: the C compiler begin used
    build_path: directory for temporary build files
    test_path: The path where the tests are kept
"""
import pytest
from pathlib import Path
from config import CONFIG
from cohort import get_cohort,current_cohort_name

pytest_plugins = ["vhdl_test", "mock_test", "python_test"]

NODEID_LENGTH_TRESHOLD = 60

def pytest_runtest_logreport(report):
    if len(report.nodeid) > NODEID_LENGTH_TRESHOLD:
        report.nodeid = ".../" + Path(report.nodeid).name

def pytest_addoption(parser):
    parser.addoption("--cohort",
                     action="store",
                     default=current_cohort_name())
    parser.addoption("--student", action="store", default="solution")
    parser.addoption("--c-compiler", action="store", default="gcc")


def pytest_configure(config):
    config.addinivalue_line("markers", "slow: mark test as slow")


@pytest.fixture
def cohort(request):
    "The cohort where student is to be found - specified using --cohort option"
    name = request.config.getoption("--cohort")
    return get_cohort(name)


@pytest.fixture
def student(request, cohort):
    "The current student under test - specified using --student option"
    name = request.config.getoption("--student")
    return cohort.student(name)


@pytest.fixture
def compiler(request):
    "The C Compiler to use"
    return request.config.getoption("--c-compiler")


@pytest.fixture
def build_path():
    "Directory path for out of source build (executables, libs and object files)"
    return CONFIG.build_path


@pytest.fixture
def test_path(cohort):
    "Directory path containing test files"
    return cohort.test_path


# @pytest.fixture(autouse=True)
# def run_before_and_after_tests(build_dir,request):
#     """Fixture to execute asserts before and after a test is run"""
#     build_dir.mkdir(exist_ok=True) # ensure build directory exists
#     yield # Run test
#     #TearDown
#     testname = request.node.name
#     #outcome=request.node.result_call.outcome
#    # print("Test:",testname,"--",outcome)
