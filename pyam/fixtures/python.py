# Copyright 2023, Dr John A.R. Williams
# SPDX-License-Identifier: GPL-3.0-only
"""
Fixtures for testing students Python scripts and functions
"""
import sys
import pytest
from subprocess import run
from pathlib import Path
from typing import Union
import importlib
import re


class PythonRunError(Exception):
    "Base Python related errors"

class PythonStyleError(Exception):
    "pylint Score too low"

@pytest.fixture
def run_script(student,request):
    """*Fixture*: A function to run a students python script.
    
    The function takes the following arguments

    Args:
      script (str): The nname of the script in the students directory.
      stdin (Union[List[str],str]): A string that will be fed to standard input to the script. Alternatively 
        a list of strings can be given - these will be joined with a newline character.
    
    Raises:
        PythonRunError: if script fails to run. Error will have stderr output from script execution.

    Returns:
        The stdout from the script as a string.

    """

    marker = request.node.get_closest_marker("timeout")
    timeout=10.0 if marker is None else marker.args[0]
    def _run_script(script,stdin):
        # pylint: disable=W1510
        if not(isinstance(stdin,str)):
            stdin="\n".join([str(a) for a in stdin])+"\n"
        result = run([sys.executable,student.path/script],capture_output=True,timeout=timeout,text=True,input=stdin)
        if result.returncode !=0:
            raise PythonRunError(result.stderr)
        return result.stdout.strip()
    
    return _run_script

@pytest.fixture
def module_name(student):
    """*Fixture*: Module name under students directory to load for a test. **Must be set in the test**"""

@pytest.fixture
def student_module(student,module_name):
    """*Fixture*: Returns the student module instance from the :func:`module_name` in the students directory."""
    spec = importlib.util.spec_from_file_location(module_name, student.path / (module_name+".py"))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

def python_lint(python_file: Path, score_threshold: int):
    """Run pylint on sudents code.
    
    Args:
      python_file: the path to the file to be checked
      score_threshold: the minimum thresold (/10) for the code to past this test.

    Raises:
      PythonRunError: If pylint returns a Fatal or Error return code
      PythonStyleError: If they do nor meet the minimum threshold.
    """
    # pylint: disable=W1510
    result = run(("pylint", python_file), capture_output=True, text=True)
    
    if ((result.returncode & 1) | (result.returncode & 2)): # Fatal or Error Python return codes
        raise PythonRunError(result.stdout+result.stderr)
    score=float(re.search(r"([-\d\.]+)/10",result.stdout).group(1))
    if score<10.0:
        print(result.stdout)
    if score<score_threshold:
        raise PythonStyleError(f"Code Rating of {score} lower than {score_threshold}")
