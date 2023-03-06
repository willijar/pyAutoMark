# Copyright 2023, Dr John A.R. Williams
# SPDX-License-Identifier: GPL-3.0-only
"""pytest fixtures to support running C (mock) tests using mocking.

This set of fixtures assumes a single student C file, and a single mock test C file.
include path will be set to the cohort test directory, the build directory and the students
directory. A file "student.h" is written into build directory to include the students c file
in the mock test.
"""

from pathlib import Path
from typing import Sequence,Union,List
from subprocess import run
import pytest
import pyam.cunit as cunit


@pytest.fixture
def binary_name() -> str:
    "*Fixture*: The binary Executable name to use for compiled tests - file will be created in build folder"
    return "mock_test"


@pytest.fixture
def student_c_file() -> Union[str,Path]:
    "*Fixture*: for the student C file currently under test. *Must be set in the test*."


@pytest.fixture
def mock_c_file() -> Union[str,Path]:
    "*Fixture*: The mock code C file currently under test. *Must be set in the test*."


@pytest.fixture(autouse=True)
def write_header(build_path, student_c_file) -> Path:
    """*Fixture*:  creates :file:`student.h` which includes the :func:`student_c_file`
    
    Used in Mock C code to include the students file."""
    header = build_path / "student.h"
    with open(header, "w") as fid:
        fid.write(f'#include "{student_c_file}"')
    return header


@pytest.fixture
def compile_flags() -> Sequence[str]:
    "*Fixture*: A list of additional compile flags (style) to use across tests"
    return [
        "-funsigned-char", "-funsigned-bitfields", "-fpack-struct",
        "-fshort-enums", "-Wall", "-std=gnu99"
    ]


@pytest.fixture
def c_compile(student, test_path, build_path, mock_c_file,
              student_c_file,binary_name,
              compile_flags, compiler):
    """*Fixture*: The compile function
    
    The returned function takes the following arguments

    Args:
        declarations (Sequence[str]): The list of declarations (defines) to
            be set for the compilation.
            Typically only one will be set to select the test in the mock C file.
        source (Union[Path,str]): source C file - defaults to mock_c_file or student_c_file

    Returns:
        Path: Location of binary executable

    Raises:
        cunit.CompilationError: (after printing captured io to stdout)
    """

    def _compile(declarations: Sequence[str] = (),
                 source: Union[Path,str] = mock_c_file or student_c_file):
        try:
            return cunit.c_compile(
                build_path / binary_name,
                source=source,
                include=[test_path, build_path, student.path],
                declarations=declarations,
                cflags=compile_flags,
                compiler=compiler)
        except cunit.CompilationError as err:
            print(err)
            raise err

    return _compile


@pytest.fixture
def c_exec(request,c_compile):
    """*Fixture*: The exec function for this test suite which will compile and execute the mock C tests.
      
    Uses the timeout marker, and if set will stop student programm execution at that time.

    The returned function takes the following arguments:

    Args:
        declarations (Sequence[str]):
            The list of delcarations (defines) tobe set for the compilation. Typically only one will be set to select the test in the mock C file.
        binary Union[Path,str]: Path to binary.
            If not specified source will be compiled first.
        input: A string that will be fed to standard input or
           a list of strings can be given - these will be joined with a newline character.

    Returns:
         The stdout from the script as a string.
    """
    marker = request.node.get_closest_marker("timeout")
    timeout=None if marker is None else marker.args[0]
    def _exec(declarations: Sequence[str] = (),
              binary: Union[Path,str] = None,
              input: Union[List[str],str] = "",
              print_cap = True):
        try:
            if binary==None:
                binary=c_compile(declarations)
            return cunit.c_exec(
                binary, input=input, timeout=timeout)
        except cunit.RunTimeError as err:
            if print_cap:
                print(err.args[0].stderr+err.args[0].stdout)
            raise err

    return _exec

@pytest.fixture
def c_lint_checks() -> str:
    """*Fixture*: C -lint checks to apply. Overwwite in your test as required"""
    return "performance-*,readability-*,portability-*"

@pytest.fixture
def c_lint(student,test_path,build_path,c_lint_checks):
    """*Fixture*: A function to provide lint ouput on students C file
    
    The returned function takes the following arguments:

    Args:
       source_file (Path): Path to C source file to be checked
       man_warnings (int): Optionally maximum number of warning to accept before test
          is considered a failure.
    """
    includes=[(lambda s: f"-I{s}")(s) for s in (test_path, build_path, student.path)]

    def _c_lint(source_file, max_warnings=0):
        result = run(
            ("clang-tidy", student.path/source_file, f"-checks={c_lint_checks}", "--quiet",
              "--", *includes),
              capture_output=True,
              text=True)
        print(result.stdout[0:])
        if result.returncode == 0:
            count=int(result.stderr.split(" ")[0])
            if count>max_warnings:
                raise cunit.LintError(result.stderr)
        else:
            raise cunit.CompilationError(result.stderr)
        
    return _c_lint

   # e.g. clang-tidy Q2b.c -checks=* --quiet -- -I../../../tests/2022/
