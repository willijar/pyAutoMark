import sys
import pytest
from subprocess import run
import importlib
import re


class PythonRunError(Exception):
    "Base Python related errors"

class PythonStyleError(Exception):
    "pylint Score too low"

@pytest.fixture
def run_script(student,request):
    """Return script runner function for this student"""

    marker = request.node.get_closest_marker("timeout")
    timeout=10.0 if marker is None else marker.args[0]
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

def python_lint(python_file, score_threshold):
    "Return function to provide pylint diagnostics on sutdents code"
    # pylint: disable=W1510
    result = run(("pylint", python_file), capture_output=True, text=True)
    print(result.stdout)
    if ((result.returncode & 1) | (result.returncode & 2)): # Fatal or Error Python return codes
        raise PythonRunError(result.stderr)
    score=float(re.search(r"([-\d\.]+)/10",result.stdout).group(1))
    if score<score_threshold:
        raise PythonStyleError(f"Code Rating of {score} lower than {score_threshold}")
    
# need to think about timeouts for python code - with windows too (signal will notn work)
# @contextmanager
# def timeout(duration):
#     def timeout_handler(signum, frame):
#         raise TimeoutError(f'block timedout after {duration} seconds')
#     signal.signal(signal.SIGALRM, timeout_handler)
#     signal.alarm(duration)
#     try:
#         yield
#     finally:
#         signal.alarm(0)

# def sleeper(duration):
#     time.sleep(duration)
#     print('finished')
