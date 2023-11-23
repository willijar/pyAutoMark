#!/usr/bin/env python3
# Copyright 2023, Dr John A.R. Williams
# SPDX-License-Identifier: GPL-3.0-only
"""Main Routine for github-retirieve command"""
import argparse
from datetime import datetime
import pyam.files
from pyam.config import CONFIG
from pyam.cohort import get_cohort, current_academic_year


def add_args(parser=argparse.ArgumentParser(description=__doc__)):
    "Parse and return args for this script"
    parser.add_argument('-c',
                        '--cohort',
                        default=CONFIG.get("cohort", current_academic_year()),
                        help="Name of student cohort")
    parser.add_argument('--until', 
                        default=None,
                        type=lambda s: datetime.strptime(s,'%Y/%m/%d %H:%M'),
                        help="If specified will checkout out last repository before given date - format Y/M/D H:M. This may be a headless checkout."
                        )
    parser.add_argument('--branch', 
                        default=None,
                        help="If specified checkout repositories to specified branch"
                        )
    parser.add_argument('-s',
                        '--students',
                        nargs="*",
                        help='Names of specific student for which tests are to be run')
    parser.add_argument("--no-reset", 
                        action="store_true",
                        help="If specified then local repositories won't be reset before a pull.")


def main(args=None):
    """Retrieve files from student repositories on github (classroom).

    Cohort manifest be configured with:
       github.template:
         The name of the template repository (prefix for student repositories)
       github.url:
         URL to github organisation where repositories reside
       github.branch:
         Name of students main branch

    Students must have 'Github Username' field in csv file."""
    if args is None:
        parser = argparse.ArgumentParser(description=__doc__)
        add_args(parser)
        args = parser.parse_args()
    cohort = get_cohort(args.cohort)
    cohort.start_log_section(f"Github retrieve {args.students or 'all'}")
    students = cohort.students(args.students)
    submission_dates = {}
    for student in students:
        student.github_retrieve(reset=not(args.no_reset),branch=args.branch) # yeh double negative
        submission_dates[student.username] = student.github_lastcommit()
        if args.until:
            student.checkout(until=args.until,branch=args.branch)
    column_name = cohort.get("student-column.submission-date")
    pyam.files.set_csv_column(cohort.path / "students.csv", column_name,
                              "Username",
                              lambda x: submission_dates.get(x, None))


if __name__ == "__main__":
    main()
