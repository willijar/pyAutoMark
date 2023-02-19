import sys
import pytest
from subprocess import PIPE, STDOUT, run
import importlib


class PythonRunError(Exception):
    "Base Python related errors"

@pytest.fixture
def timeout():
     """Timeout for scripts"""
     return 5

@pytest.fixture
def run_script(student,timeout):
    """Return script runner function for this student"""
    def _run_script(script,stdin):
        """Run named script with stdin as input, returing the subprocess result. Test Case fails if script fails to run.
        stdin can be a string or a list of items which will sent with newlines added as input to script.
        Returns script output"""
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
    """Module name under test"""

@pytest.fixture
def student_module(student,module_name):
    """Return function to import a module from a student file - returns module instance"""
    spec = importlib.util.spec_from_file_location(module_name, student.path / (module_name+".py"))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module