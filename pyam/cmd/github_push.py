#!/usr/bin/env python3
# Copyright 2023, Dr John A.R. Williams
# SPDX-License-Identifier: GPL-3.0-only
"""Main ROtine for github-retirieve command"""
import argparse
from pyam.config import CONFIG
from pyam.cohort import get_cohort, current_academic_year
from pyam.files import PathGlob

def add_args(parser=argparse.ArgumentParser(description=__doc__)):
    "Parse and return args for this script"
    parser.add_argument('-c',
                        '--cohort',
                        default=CONFIG.get("cohort", current_academic_year()),
                        help="Name of student cohort")
    parser.add_argument(
        '-s',
        '--students',
        nargs="*",
        help='Names of specific student for which tests are to be run')
    parser.add_argument("--no-reset", 
                        action="store_true",
                        help="If specified then local repositories won't be reset and retrieved before a push."),
    parser.add_argument("-b", "--branch", help="Name of branch to push to (if different from main"),
    parser.add_argument(
        "-m", "--message",
        default="Push files from tutor",
        help="Commit message to use." )               
    parser.add_argument(
        '--subdir',
        default=None,
        help="Subdirectory in student repository to push files into")
    parser.add_argument(
        dest = "files", 
        nargs=argparse.REMAINDER,
        action=PathGlob,
        default=None,
        help="List of files for directories to push")
    


def main(args=None):
    """Push files into student repositories on github (classroom).

    Cohort manifest be configured with:
       github.template:
         The name of the template repository (prefix for student repositories)
       github.url:
         URL to github organisation where repositories reside

    Students must have 'Github Username' field in csv file."""
    if args is None:
        parser = argparse.ArgumentParser(description=__doc__)
        add_args(parser)
        args = parser.parse_args()
    cohort = get_cohort(args.cohort)
    cohort.start_log_section(f"Github push {args.students or 'all'}")
    cohort.start_log_section(f"Pushing {args.files}")
    students = cohort.students(args.students)
    for student in students:
        student.github_push(files=args.files, subdir=args.subdir, reset=not(args.no_reset), branch=args.branch, msg=args.message)


if __name__ == "__main__":
    main()