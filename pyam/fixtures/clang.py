# Copyright 2023, Dr John A.R. Williams
# SPDX-License-Identifier: GPL-3.0-only
"""pytest fixtures to support running C (mock) tests using mocking.

This set of fixtures assumes a single student C file, and a single mock test C file.
include path will be set to the cohort test directory, the build directory and the students
directory. A file "student.h" is written into build directory to include the students c file
in the mock test.
"""

import re
from pathlib import Path
from typing import Sequence,Union,List
from subprocess import run
import pytest
import pyam.cunit as cunit
import pyam.cohort
from pyam.config import CONFIG


@pytest.fixture
def binary_name(student_c_file,mock_c_file) -> str:
    "*Fixture*: The binary executable name to use for compiled tests - file will be created in build folder"
    return (mock_c_file or student_c_file).stem

@pytest.fixture
def c_binary(student_c_file,mock_c_file,c_compile) -> Path:
    "*Fixture*: Path to students executable under test (or None if a Mock test)"
    if not(mock_c_file):
        return c_compile(source=student_c_file)

@pytest.fixture
def student_c_file() -> Union[str,Path]:
    "*Fixture*: for the student C file currently under test. *Must be set in the test*."


@pytest.fixture
def mock_c_file() -> Union[str,Path]:
    "*Fixture*: The mock code C file currently under test. *Must be set in the test if using mocks*."


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
def c_exec(request,c_compile,c_binary):
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
              binary: Union[Path,str] = c_binary,
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
        if result.returncode == 0:
            count=int(result.stderr.split(" ")[0])
            if count<10.0:
                print(result.stdout[0:])
            if count>max_warnings:
                raise cunit.LintError(result.stderr)
        else:
            raise cunit.CompilationError(result.stdout+result.stderr)
        
    return _c_lint

def pytest_collect_file(parent, path) -> List:
    """Hook into pytest
    
    These are C files that start with test_ and 
    contain #DEFINE PYAM_CTEST fileglob
    definition where fileglob will match a students file

    They may also contain a #DEFINE PYAM_CLINT n,expr
    definition to run a CLANG_TIDY test 
    

    Tests are recognised as symbols matching "TEST_[A-Z0-9_]+"
    
    Returns:
        List of  tuples of filepath and a list of tests declarations.
    """
    path=Path(path)
    if path.suffix == ".c" and path.name.startswith("test_"):
        text=path.read_text()
        if re.search(r'#define\s+PYAM_CTEST\s+\"(.*)\"',text):
            return CTestFile.from_parent(parent=parent,path=path,text=text)
    
    # files=[]
    # for file in test_path.glob("*.c"):
    #     text=file.read_text()
    #     if re.search(r"#include\s+<student\.h>",text):
    #         print(file)
    #         tests=re.findall("TEST_[A-Z0-9_]+",text)
    #         if tests:
    #             files.append((file,tests))
    # return files

class CTestFile(pytest.File):
    """
    A custom file handler class for C unit test files.

    Attributes:
        ctest_glob: The string from #define PYAM_CTEST "glob" - glob to find student file
        clint_threshold: Numeric threshold value from #define PYAM_CLINT theshold,"checks"
        clint_checks: Lint checks from   #define PYAM_CLINT threshold,"checks"
        cohort: Student cohort under for test
        student: student under test
        test_file_path: first file in student directory matching glob

    """
    re_CTEST=re.compile(r'#define\s+PYAM_CTEST\s+\"(.*)\"')
    re_CLINT=re.compile(r'#define\s+PYAM_CLINT\s+(\d+)(,\"(.*)\")?')
    # attributes from initialisation
    text: str
    ctest_glob: str
    clint_threshold: int = 0
    clint_checks: str
    # attributes after configure
    cohort: pyam.cohort.Cohort = None
    student: pyam.cohort.Student = None
    test_file_path: Path
    compile_file_path: Path

    @classmethod
    def from_parent(cls,parent,path,text):
        self=super().from_parent(parent=parent,path=path)
        self.text=text
        self.ctest_glob=self.re_CTEST.search(text).group(1)
        match=self.re_CLINT.search(text)
        self.clint_threshold=int(match.group(1))
        self.clint_checks=match.group(3) or "performance-*,readability-*,portability-*"
        return self
        
    # TODO: Implement init-run , c_exec and c-lint funcitonality for CTestItem and CLintItem

    def collect(self):
        """
        Overridden collect method to collect the results from each
        C Mock unit test executable.

        """
        print("Collecting from ",self.ctest_glob)
        if self.ctest_glob:
            for test in re.findall("TEST_[A-Z0-9_]+",self.text):
                yield CTestItem.from_parent(name=test,parent=self)
            if self.clint_threshold:
                yield CLintItem.from_parent(name="STYLE",parent=self)

    def configure(self,config):
        if self.cohort: #already configured
            return
        self.cohort=pyam.cohort.get_cohort(config.getoption("--cohort"))
        self.student=self.cohort.students(config.getoption("--student"))
        paths=list(self.student.path.glob(self.ctest_glob))
        print("Paths=",paths)
        if not paths:
            self.cohort.log("No CTest file matching '%s' found for %s",self.ctest_glob,self.student.name())
            raise FileNotFoundError(self.student,self.ctest_glob)
        self.test_file_path=paths[0]
        if len(paths)>1:
            self.cohort.log("Multiple CTest files matching '%s' found for %s, using %s",
                            self.ctest_glob,self.student.name(), self.test_file_path)
        #insert include to student file
        self.compile_file_path=CONFIG.build_path/self.path.name
        with open(self.compile_file_path,"w") as fid:
            fid.write(f'#include "{self.test_file_path}"\n')
            fid.write(self.text)
            
    def includes(self):
        return (self.cohort.test_path,CONFIG.build_path,self.student.path)
            
    def c_compile(self,test_name):
        try:
            return cunit.c_compile(
                binary=CONFIG.build_path/self.test_file_path.stem,
                source=self.compile_file_path,
                include=self.includes(),
                cflags=["-funsigned-char", "-funsigned-bitfields", "-fpack-struct",
                        "-fshort-enums", "-Wall", "-std=gnu99"],
                declarations=[test_name])
        except cunit.CompilationError as err:
            raise err

    def c_exec(self,test_name):
        binary=self.c_compile(test_name)
        try:
            cunit.c_exec(self.c_compile(test_name))
        except cunit.RunTimeError as err:
            raise err

    def c_lint(self):
        includes=[(lambda s: f"-I{s}")(s) for s in self.includes()]
        result = run(
            ("clang-tidy", self.test_file_path, f"-checks={self.clint_checks}", "--quiet",
              "--", *includes),
              capture_output=True,
              text=True)
        if result.returncode != 0:
            raise cunit.CompilationError(result.stdout+result.stderr)
        count=int(result.stderr.split(" ")[0])
        if count>0 and count<=self.clint_threshold: 
             print(result.stdout[0:])
        if count>self.clint_threshold:
            raise cunit.LintError(result.stdout)
    
class CTestItem(pytest.Item):
    """
    Pytest.Item subclass to handle each test result item. 
    """
   
    def runtest(self):
        """Execute file"""
        self.parent.c_exec(self.name)

    def repr_failure(self, excinfo):
        """Called when self.runtest() raises an exception."""
        if isinstance(excinfo.value, cunit.RunTimeError) or isinstance(excinfo.value, cunit.CompileTimeError):
            return excinfo.value.args[0].stderr+excinfo.value.args[0].stdout

    def reportinfo(self):
        return self.parent.test_file_path.stem, 0, self.parent.test_file_path.stem+":"+self.name
    
class CLintItem(pytest.Item):
    """
    Pytest.Item subclass to handle each test result item. 
    """
   
    @pytest.mark.usefixtures("c_exec")
    def runtest(self):
        """Execute file"""
        self.parent.c_lint()

    def repr_failure(self, excinfo):
        """Called when self.runtest() raises an exception."""
        if isinstance(excinfo.value, cunit.LintError):
            return excinfo.value.args[0]

    def reportinfo(self):
        return self.parent.test_file_path.stem, 0, self.parent.test_file_path.stem+":"+self.name

def pytest_collection_modifyitems(config, items):
    for item in items:
       if isinstance(item,CTestItem) or isinstance(item,CLintItem):
           item.parent.configure(config)



   # e.g. clang-tidy Q2b.c -checks=* --quiet -- -I../../../tests/2022/
