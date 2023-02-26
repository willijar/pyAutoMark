"""Implementation of write-csv command"""
import argparse
from pathlib import Path
import openpyxl
from pyam.cohort import get_cohort
from pyam.cmd.args import add_common_args
from pyam.files import set_csv_column


def main(args=None):
    """Read marks from a set of mark spreadsheets and write them into csv files"""
    if args is None:
        parser = argparse.ArgumentParser(description=__doc__)
        add_args(parser)
        args = parser.parse_args()
    cohort = get_cohort(args.cohort)
    students = cohort.students(args.students)
    cohort.start_log_section(f"Collating marks into csv files")
    marks = get_marks(cohort, students, args.prefix, args.mark_sheets)

    def get_value(student_id):
        match = None
        for student in marks:
            if student.student_id in student_id or student.username in student_id:
                match = student
                break
        if match:
            return marks.pop(match)
        cohort.log.warning("No mark found for %s", student_id)
        return None

    if not args.csv_files:
        args.csv_files = cohort.report_path.glob(f"{args.prefix}*.csv")
    for path in args.csv_files:
        set_csv_column(path, "Mark", "#Cand Key", get_value)
    for student in marks:
        cohort.log.warning("No CSV record for %s", student.name())


def get_id_and_mark(path):
    """Returns student id and mark from spreadsheet at path"""
    wbook = openpyxl.load_workbook(path,data_only=True)
    student_id = None
    mark = None
    for title, coord in wbook.defined_names["student_id"].destinations:
        student_id = wbook[title][coord].value
    for title, coord in wbook.defined_names["mark"].destinations:
        mark = wbook[title][coord].value
    return (student_id, mark)


def get_marks(cohort, students, prefix, paths) -> dict:
    """Sets  marks for a set of students from spreadsheets

    Given a list of paths, or a cohort name and prefix Returns a dictionary
    mapping student_id to marks.

    Will warn if there are missing marks or missing students."""
    if not paths:
        paths =  list(cohort.report_path.glob(f"{prefix}*.xlsx"))
    marks = {}
    for path in paths:
        if path.suffix != ".xlsx":
            cohort.log.warning("File %s is not a spreadsheet", path)
            continue
        try:
            (student_id, mark) = get_id_and_mark(path)
        except KeyError:
            continue
        found = False
        for student in students:
            if student.student_id == student_id:
                marks[student] = mark
                found = True
                break
    return marks


def add_args(parser=argparse.ArgumentParser(description=__doc__)):
    """Add and parse args for this script"""
    add_common_args(parser)
    parser.add_argument(
        '--mark-sheets',
        nargs="*",
        type=Path,
        default=[],
        help="list of mark sheets to be processed. "
        "Defaults to those in report directory with matching prefix")
    parser.add_argument('--csv-files',
                        nargs="*",
                        type=Path,
                        default=[],
                        help="List of csv files to be processed. Deafult is those starting with prefix in report directory")
    parser.add_argument(
        '--mark-col',
        help=
        "Name or number of column of csv file where marks are to be written.")
    parser.add_argument('--student-col',
                        help="Name or number of student id column in CSV file")
