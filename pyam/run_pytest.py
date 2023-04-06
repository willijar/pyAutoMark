# Copyright 2023, Dr John A.R. Williams
# SPDX-License-Identifier: GPL-3.0-only
"""Pun pytest in the cohort  context."""
import subprocess
import os
from pathlib import Path
from typing import List,Union
import pyam.fixtures

def run_pytest(cohort: 'pyam.cohort.Cohort', *extras: Union[List[str],None]) -> subprocess.CompletedProcess:
    """
    Run pytest for pyAutoMark

    Args:
        cohort: The cohort context to use

    Optional:
        extras: extra arguments to send pyttest

    Returns:
        subprocess.CompletedProcess: result of run
    """
    # pylint: disable=W1510
    #Ensure pyam is in Python search path for pytest
    env = os.environ.copy()
    sep=":"
    if os.name == "nt":
        sep=";"
    env["PYTHONPATH"] = str(Path(__file__).parent.parent.resolve()) + sep + env.get("PYTHONPATH","")
    #set up fixtures argument
    extras = list(extras)
    #Get fixtures list -either from config or all
    fixtures = cohort.get("fixtures")
    if not fixtures:
        fixtures = pyam.fixtures.__all__
    elif isinstance(fixtures, str):
        fixtures = [fixtures]
    if "common" not in fixtures:
        fixtures += ["common"]
    for fixture in fixtures:
        extras += ['-p', f"pyam.fixtures.{fixture}"]
    result = subprocess.run(("pytest", *extras, '--cohort', cohort.name),
                            text=True,
                            capture_output=True,
                            cwd=cohort.test_path,
                            env=env)
    return result
