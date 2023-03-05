# Copyright 2023, Dr John A.R. Williams
# SPDX-License-Identifier: GPL-3.0-only
"""C compilation and program execution functions

Typical Usage:

.. code-block:
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
              sources: Sequence[Union[Path,str]],
              include: Sequence[Union[Path,str]] = (),
              cflags: Sequence[str] = (),
              declarations: Sequence[str] = (),
              compiler: str = "gcc") -> Union[Path, str]:
    """Use C compile to compile source files into an executable binary

    Args:
      binary: location for binary executable
      sources: source files to compile
      include: include paths to search for headers
      cflags: additional flags to add during compilation
      declarations: list of compile declarations (-D flags)
      compiler: name of compiler to use

    Raises:
        CompilationError: if compiler failed

    Returns:
        Location of binary executable
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
    raise CompilationError(result.stdout+result.stderr)


def c_exec(binary: Union[Path, str], flags: Sequence[str]=(), timeout: Union[float,str] = None) -> True:
    """Execute a binary executable with given flags.

    Args:
        binary: Path to binary executable
        timeout: timeout for process

    Raises:
        RunTimeError: If return code is 0

    Returns:
        True
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
