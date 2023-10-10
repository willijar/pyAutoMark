# Copyright 2023, Dr John A.R. Williams
# SPDX-License-Identifier: GPL-3.0-only
# pylint: disable=W0621
"""Test Fixtures to check students VHDL designs using simulation or synthesis:

Main testing fixtures:
  :func:`vhdl_simulate`:
    returns a function to run a tutors vhdl testbench against student VHDL files
  :func:`vhdl_synthesise`:
    return a function to test synthesisis of a student VHDl design

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

import subprocess
from subprocess import run
import re
from io import StringIO
from pathlib import Path
from typing import List
from datetime import datetime
import pytest
from pyam.files import find_executable
import pyam.cohort
from pyam.config import CONFIG


class VHDLError(Exception):
    "Base for all VHDL related errors"


class VHDLAnalysisError(VHDLError):
    "Error at VHDL Analysis stage"


class VHDLRunError(VHDLError):
    "Error at chdl simulation/run time"


class VHDLSynthesisError(VHDLError):
    "Error with VHDL Synthesis"


@pytest.fixture(autouse=True)
def clean(ghdl_exec, build_path) -> None:
    "*Autouse Fixture*: Runsh ghdl --clean at start of test run"
    run((ghdl_exec, "--clean", f"--workdir={build_path}"), check=True)


@pytest.fixture
def search_paths() -> List[str]:
    "*Fixture*: A list of additional paths to search for the executables"
    return ("/usr/bin", "/opt/Xilinx/", "/usr/local/")


@pytest.fixture
def vivado_exec(search_paths) -> Path:
    "*Fixture*: Path to Vivado executable for synthesis"
    return find_executable("bin/vivado", search_paths)


@pytest.fixture
def partnumber() -> str:
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


def run_ghdl(command,
             unit=None,
             ghdl_exec="ghdl",
             options=("--std=08", "--warn-no-hide"),
             build_path="./",
             run_options=(),
             timeout=None):
    """Run the ghdl command
    Args:
      ghdl_exec (Union[Path|str]): ghdl executable
      command (str): the ghdl command string to use e.g.
        -a to analyse or --elab-run to run simulation
      options (Sequence[str]): sequence of additional options to pass to ghdl
      unit (str): the top level vhdl to execute (if running a simulation)
      run_options (Sequence[str]): Additional run time ghdl options to give after unit
      build_path Union[Path|str]): Path where test executable is to be built
      timeout (Union[float|None]): maximum execution time for the run

    Returns:
      subprocess.CompletedProcess if successful

    Raises:
      VHDLAnalysisError: if analysis (-a) command failed
      VHDLRunError: if -r or --elab-run command faild
      VHDLError: if ghdl failed but netiehr of above commands
      subprocess.TimeoutExpired
    """
    #pylint: disable=subprocess-run-check
    #DEBUG: print(ghdl_exec, command, *options, unit,*run_options)
    if unit:
        result = run([ghdl_exec, command, *options, unit,*run_options],
                    cwd=build_path,
                    text=True,
                    capture_output=True,
                    timeout=timeout)
    else:
        result = run([ghdl_exec, command],
                    cwd=build_path,
                    text=True,
                    capture_output=True,
                    timeout=timeout)
    if result.returncode != 0:
        msg = result.stdout + result.stderr
        if command == "-a":
            raise VHDLAnalysisError(msg)
        if command in ("--elab-run", "-r"):
            raise VHDLRunError(msg)
        raise VHDLError(f"GHDL '{unit}' {msg}")
    return result


@pytest.fixture
def ghdl(ghdl_exec, ghdl_options, build_path, request):
    """*Fixture*: A function to run a test using ghdl.

    The timeout marker is honoured to limit maximum execution time if appropriate

    Args:
      command (str): the ghdl command string to use
        e.g. -a to analyse or --elab-run to run simulation
      options (Sequence[str]):
        sequence of additional options to pass to ghdl, defaults to ghdl_options fixture
      unit (str): the ghdl unit to execute command on
      run_options (Sequence[str]): Additional run time ghdl options to give after unit

    Raises:
      VHDLAnalysisError: if analysis failed
      VHDLRunError: if -r or --elab-run command faild
      VHDLError: if VHDL simulation failed but neither of above commands
    """
    marker = request.node.get_closest_marker("timeout")
    timeout = None if marker is None else marker.args[0]

    # pylint: disable=W1510
    def _ghdl(command, unit="", options=ghdl_options, run_options=()):
        run_ghdl(command,
                 unit=unit,
                 ghdl_exec=ghdl_exec,
                 options=options,
                 run_options=run_options,
                 build_path=build_path,
                 timeout=timeout)
        # result = run(
        #     [
        #         ghdl_exec, command, *options, f"--workdir={build_path}", unit,
        #         *run_options
        #     ],
        #     cwd=build_path,
        #     text=True,
        #     capture_output=True,
        #     timeout=timeout
        # )
        # if result.returncode != 0:
        #     msg = result.stdout
        #     if command == "-a":
        #         raise VHDLAnalysisError(msg)
        #     if command in ("--elab-run", "-r"):
        #         raise VHDLRunError(msg)
        #     raise VHDLError(f"GHDL '{unit}' {msg}")

    return _ghdl


@pytest.fixture
def vhdl_simulate(ghdl, student, test_path):
    """*Fixture*: A function to analyse student against tutors testbench.
    Uses ghdl fixture to run synthesis

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
            assert True, err.args[0]

    return _vhdl_simulate

def bitfile_properties(file):
    """Given a path to a bitfile return the file UserID and date in a dictionary
    - Linux only"""
    properties=subprocess.run(("file",  file), text=True, check=True, capture_output=True,).stdout
    userid=re.search(r";UserID=([^;]+)",properties).group(1)
    datestr=re.search(r"built\s+([^\s]+)",properties).group(1)
    date=datetime.strptime(datestr,"%Y/%m/%d(%H:%M:%S)")
    return {"UserID": userid, "Date": date}

@pytest.fixture
def vivado_options() -> List[str]:
    "*Fixture*:  return additional vivado options to use on tests"
    return ("-nojournal", )


@pytest.fixture
def vivado(request, vivado_exec, build_path, student, vivado_options,
           partnumber):
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
    timeout = None if marker is None else marker.args[0]

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
        no_errors=0
        errors=[]
        # collect all unique error lines
        for line in list(dict.fromkeys(result.stdout.splitlines())):
            if "ERROR:" in line:
                no_errors+=1
                errors.append(line)
            if "CRITICAL WARNING" in line:
                errors.append(line)
        if no_errors!=0:
            raise AssertionError("\n".join(errors))
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
        bitfile = vivado(build_path / f"{top}.bit", top, files,
                         (f"{student.path}/{constraints_file}",))
        assert bitfile.exists(), "No bitfile Generated"

    return _vhdl_synthesise


def pytest_collect_file(parent, path) -> List:
    """Hook into pytest

    These are VHDL files that start with test_ and
    contain "-- PYAM_TEST fileglob" comment
    definition where fileglob will match students files

    They may also contain a -- PYAM_TIMEOUT <float

    Multiple tests can be instantiated per testbench using a PYAM_TEST generic,
    Where the values are specified in a -- PYAM_TEST_VALUES comment

    Tests are recognised as symbols matching "TEST_[A-Z0-9_]+"

    A test timeout may be specified using -- PYAM_TIMEOUT <float>

    Returns:
        List of  tuples of filepath and a list of tests declarations.
    """
    path = Path(path)
    if path.suffix == ".vhd" and path.name.startswith("test_"):
        text = path.read_text(encoding="ascii")
        if re.search(r'--\s+PYAM_TEST\s+\"(.*)\"', text):
            return VHDLTestFile.from_parent(parent=parent,
                                            path=path,
                                            text=text)
    return None


class VHDLTestFile(pytest.File):
    """
    A custom file handler class for VHDL unit test files.

    Attributes:
        text (str): The text of the file under test
        test_globs (str): The string from -- PYAM_TEST "glob"+ - glob sto find student file(s)
        timeout (fload): timout in seconds specified using -- PYAM_TIMEOUT <float>
        tests (list): List of tests to be performed set usuing -- PYAM_TEST_VALUE value
              These will be passed as PYAM_TEST generci value using -gPYAM_TEST=VALUE
              If not specified file is executed as a single test item
        cohort: Student cohort under for test
        student: student under test
        uut_path (Path): first file in student directory matching glob
    """
    RE_TEST = re.compile(r'--\s+PYAM_TEST\s+\"(.*?)\"(?:[,\s]+\"(.*)\")*')
    RE_TIMEOUT = re.compile(r'--\s+PYAM_TIMEOUT\s+(.+)')
    RE_TEST_VALUE = re.compile(r'--\s+PYAM_TEST_VALUE\s+(.+)$')
    RE_DEPENDS = re.compile(r'--\s+PYAM_DEPENDS\s+\"(.*?)\"(?:[,\s]+\"(.*)\")*')
    # attributes from initialisation
    text: str
    test_globs: List[str]
    test_timeout = None
    test_values = []
    test_depends = []
    # attributes after configure
    cohort: pyam.cohort.Cohort = None
    student: pyam.cohort.Student = None
    uut_paths: List[Path]

    @classmethod
    def from_parent(cls, parent, *, fspath=None, path=None, text="", **kw):
        """Class constructor as required by pytest"""
        self = super().from_parent(parent=parent, fspath=fspath, path=path, **kw)
        self.text =  text
        self.test_globs = self.RE_TEST.findall(self.text)[0]
        match = self.RE_TIMEOUT.search(self.text)
        if match:
            self.test_timeout = float(match.group(1))
        self.test_values = self.RE_TEST_VALUE.findall(self.text)
        match = self.RE_DEPENDS.findall(self.text)
        if match:
            self.test_depends=match[0]
        return self

    def collect(self):
        """
        Overridden collect method to collect the results from a vhdl file.
        If PYAM_TEST_VALUEs are specified these will be used
        """
        if self.test_values:
            for test in self.test_values:
                yield VHDLTestItem.from_parent(parent=self, name=test, test=test)
        else:
            yield VHDLTestItem.from_parent(parent=self, name=self.path.name)

    def configure(self, config):
        """Set up this VHDLTestFIle from configuration information once it is available

            Only done once per file - retrieve cohort and student context and file under test
        """
        if self.cohort:  #already configured
            return
        self.cohort = pyam.cohort.get_cohort(config.getoption("--cohort"))
        if not config.getoption("--student"):
            return # if no student collecting tests only
        self.student = self.cohort.students(config.getoption("--student"))
        self.uut_paths=[]
        for glob in self.test_globs:
            if glob:
                paths = list(self.student.path.glob(glob))
                if not paths:
                    self.cohort.log("No VHDL Test file matching '%s' found for %s",
                                    glob, self.student.name())
                    raise FileNotFoundError(self.student, glob)
                self.uut_paths.append(paths[0])
                if len(paths) > 1:
                    self.cohort.log(
                        "Multiple VHDL Test files matching '%s' found for %s: using %s",
                        glob, self.student.name(), self.uut_paths)


    def run_test(self, item):
        "Run a VHDL test item"
        # analyse test dependencies before running tests
        #DEBUG: print("VHDL Test File", self.path)
        #DEBUG: print("UUT Fles:",self.uut_paths)
        run_ghdl("--remove")
        for filename in self.test_depends:
            if filename:
                run_ghdl(command="-a", unit=self.path.with_name(filename),
                         build_path=CONFIG.build_path,
                         timeout=self.test_timeout)
        run_options = []
        if item.test_generic:
            run_options = ["-gPYAM_TEST_VALUE={item.test_generic}"]
        run_ghdl(command="-a", unit=self.path,
                 build_path=CONFIG.build_path,
                 timeout=self.test_timeout)
        for uut in self.uut_paths:
            if uut:
                run_ghdl(command="-a",
                        unit=uut,
                        build_path=CONFIG.build_path,
                        timeout=self.test_timeout)
        run_ghdl(command="--elab-run",
                 unit=self.path.stem,
                 build_path=CONFIG.build_path,
                 run_options=["--assert-level=error", *run_options],
                 timeout=self.test_timeout)


class VHDLTestItem(pytest.Item):
    """Pytest.Item subclass to handle each test result item."""

    test_generic = None

    @classmethod
    def from_parent(cls, parent, **kw):
        self = super().from_parent(parent=parent, **kw)
        self.test_generic = kw.get("test", None)
        return self

    def runtest(self):
        """Execute file"""
        self.parent.run_test(self)

    def repr_failure(self, excinfo, style=None):
        """Called when self.runtest() raises an exception."""
        if isinstance(excinfo.value, VHDLError):
            return excinfo.value.args[0]
        if isinstance(excinfo.value, subprocess.TimeoutExpired):
            return f"Timeout Expired: {excinfo.value.args[1]}s"
        return super().repr_failure(excinfo, style)

    def reportinfo(self):
        if self.test_generic:
            return self.parent.path, 0, f"{self.parent.path.stem}[{self.test_generic}]"
        return self.parent.path, 0, f"{self.parent.path.stem}"

def pytest_collection_modifyitems(config, items):
    """Ensure that if we have a test item that the file collector is configured"""
    for item in items:
        if isinstance(item, VHDLTestItem):
            item.parent.configure(config)
