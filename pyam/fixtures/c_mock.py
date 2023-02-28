# Copyright 2023, Dr John A.R. Williams
# SPDX-License-Identifier: GPL-3.0-only
"""pytest fixtures to support running C tests using mocking

Fixtures:
    binary_name: Path for executable
    student_c_file: Path to student C file under test
    mock_c_file: path to the mock C file with tests
    compile_flags (Sequence[str]): Additional flags to use during compilation
    c_compile: Function which takes sequence of declarations to compile mock test
    c_exec: Function to execute and compile mock test, given list of declarations
"""

from pathlib import Path
from typing import Sequence
from subprocess import run
import pytest
import pyam.cunit as cunit


@pytest.fixture
def binary_name() -> str:
    "Binary Executable name to use for compiled tests"
    return "mock_test"


@pytest.fixture
def student_c_file() -> str:
    "student C file currently under test - should be set in module or class"


@pytest.fixture
def mock_c_file() -> str:
    "The mock code C file currently under test - should be set in module or class"


@pytest.fixture(autouse=True)
def write_header(build_path, student_c_file) -> Path:
    "Setup up header file to include students c_file - return path of the generated header file"
    header = build_path / "student.h"
    with open(header, "w") as fid:
        fid.write(f'#include "{student_c_file}"')
    return header


@pytest.fixture
def compile_flags() -> Sequence[str]:
    "List of additional compile flags (style) to use across tests"
    return [
        "-funsigned-char", "-funsigned-bitfields", "-fpack-struct",
        "-fshort-enums", "-Wall", "-std=gnu99"
    ]


@pytest.fixture
def c_compile(student, test_path, build_path, mock_c_file, binary_name,
              compile_flags, compiler):
    "Return compile function for this test suite which takes declarations as argument"

    def _compile(declarations: Sequence[str] = ()):
        try:
            return cunit.c_compile(
                build_path / binary_name,
                sources=[mock_c_file],
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
    "Return Exec function for this test suite which takes declarations as argument"
    marker = request.node.get_closest_marker("timeout")
    timeout=None if marker is None else marker.args[0]
    def _exec(declarations: Sequence[str] = ()):
        try:
            return cunit.c_exec(c_compile(declarations),timeout=timeout)
        except cunit.RunTimeError as err:
            print(err)
            raise err

    return _exec

@pytest.fixture
def c_lint_checks():
    """Return C -lint checks to appy - default is * (all)"""
    return "*"

@pytest.fixture
def c_lint(student,test_path,build_path,c_lint_checks):
    "Return function to provide lint ouput on students C file"
    includes=[(lambda s: f"-I{s}")(s) for s in (test_path, build_path, student.path)]

    def _c_lint(source_file, max_warnings=0):
        result = run(
            ("clang-tidy", student.path/source_file, f"-checks={c_lint_checks}", "--quiet",
              "--", *includes),
              capture_output=True,
              text=True)
        print(result.stdout)
        
        if result.returncode == 0:
            count=int(result.stderr.split(" ")[0])
            if count>max_warnings:
                raise cunit.LintError(result.stderr)
        else:
            raise cunit.CompilationError(result.stderr)
        
    return _c_lint

   # clang-tidy Q2b.c -checks=* --quiet -- -I../../../tests/2022/
