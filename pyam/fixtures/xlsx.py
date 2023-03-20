
"""Test Fixtures to check students xlsx spreadsheet submissions:

Support fixtures:
  workbook: students workbook
  solution_workbook: The workbook for the solution

Configuration fixtures:
  student_xlsx_file: relative path for students submission xlsx file
"""

from pathlib import Path
from typing import Union
import pytest
import openpyxl


@pytest.fixture
def student_xlsx_file(cohort) -> str:
    "*Fixture*: Name of the student workbook. *Must be set in the test*."
    return cohort["workbook"]

@pytest.fixture
def workbook(student,student_xlsx_file) -> openpyxl.Workbook:
    "*Fixture*: The workbook object under test"
    return openpyxl.load_workbook(student.file(student_xlsx_file), data_only=True)

@pytest.fixture
def solution_workbook(solution,student_xlsx_file) -> openpyxl.Workbook:
    "*Fixture*: The exemplar/reference workbook for answers"
    if solution:
        return openpyxl.load_workbook(solution.file(student_xlsx_file), data_only=True)



