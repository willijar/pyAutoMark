# Copyright 2023, Dr John A.R. Williams
# SPDX-License-Identifier: GPL-3.0-only
"""C compilation and program execution functions

Typical Usage:

binary_path=c_compile(binary_path,"mysouce.c",include=["include_path"],declarations=['DOSOMETHING'])
ran_ok=c_exec(binary_path, options=( "option1", "option2" ), timeout=5)
"""

from pathlib import Path
from subprocess import run
from typing import Union, Sequence


class CompilationError(Exception):
    """Error in C compilation"""


class RunTimeError(Exception):
    """Error in binary executation"""

class LintError(Exception):
    """Exceeded maximum number of lint warnings"""


def c_compile(binary: Union[Path, str],
              sources: Sequence,
              include: Sequence = (),
              cflags: Sequence = (),
              declarations: Sequence = (),
              compiler: str = "gcc") -> Union[Path, str]:
    """Use C compile to compile source files into an executable binary

    Args:
      binary (Union[Path, str]): location for binary executable
      sources (Sequence): source files to compile
      include (Sequence): include paths to search for headers
      cflags (Sequence) : additional flags to add during compilation
      declarations (Sequence): list of compile declarations (-D flags)
      compiler (str)    : name of compiler to use

    Raises:
        CompilationError: if compiler failed

    Returns:
        binary: Location of binary executable
    """
    # pylint: disable=W1510
    sources = [str(s) for s in sources]
    include = [(lambda s: f"-I{s}")(s) for s in include]
    for dec in declarations:
        cflags = cflags + ["-D", dec]
    result = run(
        (compiler, *cflags, "-o",
         str(binary), *include, *sources),
        text=True,
        capture_output=True
    )
    if result.returncode == 0:
        return binary
    raise CompilationError(result.stdout)


def c_exec(binary: Union[Path, str], flags=(), timeout: float = None):
    """Execute a binary executable with given flags.

    Args:
        binary (Union[Path, str]): Path to binary executable

    Raises:
        RunTimeError: If return code is 0
    """
    # pylint: disable=W1510
    result = run(
        (str(binary), *flags),
        text=True,
        capture_output=True,
        timeout=timeout
    )
    if result.returncode != 0:
        raise RunTimeError(result.stdout+result.stderr)
    return True
