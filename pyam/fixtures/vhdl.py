# Copyright 2023, Dr John A.R. Williams
# SPDX-License-Identifier: GPL-3.0-only
# pylint: disable=W0621
"""Test Fixtures to check students VHDL designs using simulation or synthesis:

Main testing fixtures:
  :func:`vhdl_simulate`: returns a function to run a tutors vhdl testbench against student VHDL files
  :func:`vhdl_synthesise`: return a function to test synthesisis of a student VHDl design

Support fixtures:
  ghdl: returns function to run the ghdl simulator
  vivdao: run function to run Vivado

Configuration fixtures:
  search_paths: paths to dsearch for ghdl and vviado executables (if no on path)
  vivado_exec: the (found) vivado executable path
  ghdl_exec: the (found) ghdl executable path
  partnumber: Vivado parnumber to synthesise for
  ghdl_options: Standard list op options to pass ghdl
  vivado_options: standard list of options to pass vivado

"""

from subprocess import run
from io import StringIO
import pytest
from pathlib import Path
from typing import List
from pyam.files import find_executable


class VHDLError(Exception):
    "Base for all VHDL related errors"


class VHDLAnalysisError(VHDLError):
    "Error at VHDL Analysis stage"


class VHDLRunError(VHDLError):
    "Error at chdl simulation/run time"


class VHDLSynthesisError(VHDLError):
    "Error with VHDL Synthesis"


@pytest.fixture(autouse=True)
def clean(ghdl_exec, build_path) ->None:
    "*Autouse Fixture*: Runsh ghdl --clean at start of test run"
    run((ghdl_exec, "--clean", f"--workdir={build_path}"), check=True)


@pytest.fixture
def search_paths() -> List[str]:
    "*Fixture*: A list of additional paths to search for the executables"
    return ("/opt/Xilinx/", "/usr/local/")


@pytest.fixture
def vivado_exec(search_paths) -> Path:
    "*Fixture*: Path to Vivado executable for synthesis"
    return find_executable("bin/vivado", search_paths)


@pytest.fixture
def partnumber() ->str:
    "*Fixture*: Partnumber to use in synthesis"
    return "xc7a35tcpg236-1"


@pytest.fixture
def ghdl_exec(search_paths) -> Path:
    "*Fixture*: The path to the ghdl executable for VHDL simulation"
    return find_executable("ghdl", search_paths)


@pytest.fixture
def ghdl_options() -> List[str]:
    "List of additional ghdl flags (style) to use across tests"
    return ("--std=08", "--warn-no-hide")


@pytest.fixture
def ghdl(ghdl_exec, ghdl_options, build_path, request):
    """*Fixture*: A function to run a test using ghdl.

    The timeout marker is honoured to limit maximum execution time if appropriate

    Args:
      command (str): the ghdl command string to use e.g. -a to analyse or --elab-run to run simulation
      options (Sequence[str]): sequence of additional options to pass to ghdl, defaults to ghdl_options fixture
      unit (str): the ghdl unit to execute command on
      run_options (Sequence[str]): Additional run time ghdl options to give after unit

    Raises:
      VHDLAnalysisError: if analysis (-a) command failed
      VHDLRunError: if -r or --elab-run command faild
      VHDLError: if ghdl failed but netiehr of above commands
    """
    marker = request.node.get_closest_marker("timeout")
    timeout=None if marker is None else marker.args[0]
    # pylint: disable=W1510
    def _ghdl(command, unit="", options=ghdl_options, run_options=()):
        result = run(
            [
                ghdl_exec, command, *options, f"--workdir={build_path}", unit,
                *run_options
            ],
            cwd=build_path,
            text=True,
            capture_output=True,
            timeout=timeout
        )
        if result.returncode != 0:
            msg = result.stdout
            if command == "-a":
                raise VHDLAnalysisError(msg)
            if command in ("--elab-run", "-r"):
                raise VHDLRunError(msg)
            raise VHDLError(f"GHDL '{unit}' {msg}")

    return _ghdl


@pytest.fixture
def vhdl_simulate(ghdl, student, test_path):
    """*Fixture*: A function to analyse student against tutors testbench.
    Uses ghdl fixture to run simulations

    Args:
      top (str): the top level (tutors) testbench filename to run
      student_files List[str]: List of filenames in student directory to analyse first
      test_files List[str]: List of files in test directory to analyse before student files
                  e.g. to provide working implementations for student work to use

    Raises:
       see :func:`ghdl`:
"""
    def _vhdl_simulate(top, student_files, test_files=None):
        if test_files is None:
            ghdl("-a", test_path / f"{top}.vhd")
        for file in student_files:
            ghdl("-a", student.path / file)
        if test_files is not None:
            for file in test_files:
                ghdl("-a", test_path / file)
        try:
            ghdl("--elab-run", top, run_options=["--assert-level=error"])
        except VHDLError as err:
            print(str(err))
            raise(err)

    return _vhdl_simulate


@pytest.fixture
def vivado_options() -> List[str]:
    "*Fixture*:  return additional vivado options to use on tests"
    return ("-nojournal",)


@pytest.fixture
def vivado(request,vivado_exec, build_path, student, vivado_options, partnumber):
    """*Fixture* The function to run vivado synthesis tool

    Args:
      bitfile (str):filename for bitfile output in buoild directory
      top (str): Name of top level entity in design
      sources (List[Path]): vhdl source files (full paths)
      constraint (List[Path]): list of constraints files (full paths)

    Raises:
      VHDLSynthesisError: If vivado exits with an error
    """
    marker = request.node.get_closest_marker("timeout")
    timeout=None if marker is None else marker.args[0]
    def _vivado(bitfile, top, sources, constraints):
        # pylint: disable=W1510
        tcl = StringIO()
        for source in sources:
            tcl.write(f"read_vhdl {source}\n")
        for source in constraints:
            tcl.write(f"read_xdc {source}\n")
        tcl.write(f"synth_design -top {top} -part {partnumber}\n")
        tcl.write(
            "opt_design\npower_opt_design\nplace_design\nphys_opt_design\nroute_design\n"
        )
        tcl.write(f"write_bitstream -force {bitfile}\n")
        tcl = tcl.getvalue()
        result = run([
            vivado_exec, *vivado_options, "-log", build_path / "synth.log",
            "-tempDir", build_path, "-mode", "tcl"
        ],
                     cwd=student.path,
                     capture_output=True,
                     text=True,
                     timeout=timeout,
                     input=tcl)
        if result.returncode != 0:
            print(result.stdout)
            raise VHDLSynthesisError
        return bitfile

    return _vivado

@pytest.fixture
def vhdl_synthesise(student, build_path, vivado):
    """*Fixture* A function to synthesise a student vhdl design and generate a bitstream

    Args:
      top (str): Name of top level entity in design
      student_files (List[str]): list of vhdl filenames in student directory for design
      constraints_file (str): Name of students constraints file to use in design - defaul top.xdc
    
    Raises:
      FileNotFoundError: if no bitfile generated

    See also :func:`vivado`

    """

    def _vhdl_synthesise(top, student_files, constraints_file=None):
        if constraints_file is None:
            constraints_file = f"{top}.xdc"
        files = []
        for filename in student_files:
            files.append(student.path / filename)
        bitfile=vivado(build_path / f"{top}.bit", top, files,
                (f"{student.path}/{constraints_file}"))
        if not bitfile.exists():
            return FileNotFoundError(bitfile)

    return _vhdl_synthesise
