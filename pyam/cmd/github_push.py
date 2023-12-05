#!/usr/bin/env python3
# Copyright 2023, Dr John A.R. Williams
# SPDX-License-Identifier: GPL-3.0-only
"""Main Routine for github-push command"""
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
        '--student',
        help='Names of a specific student for which tests are to be run')
    parser.add_argument("--no-reset", 
                        action="store_true",
                        help="If specified then local repositories won't be reset and retrieved before a push.")
    parser.add_argument(
        "-m", "--message",
        default="Push files from tutor",
        help="Commit message to use." )               
    parser.add_argument(
        '--subdir',
        default=None,
        help="Subdirectory in student repository to push files into")
    parser.add_argument('--branch', 
                        default=None,
                        help="If specified files will be put in this branch - otherwise github.branch configuration will be used"
                        )
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
        github.branch:
            Name of students main branch

    Students must have 'Github Username' field in csv file and an assessment specified."""
    if args is None:
        parser = argparse.ArgumentParser(description=__doc__)
        add_args(parser)
        args = parser.parse_args()
    cohort = get_cohort(args.cohort)
    if args.student: args.student=[args.student]
    cohort.start_log_section(f"Github push {args.student or 'all'}")
    cohort.start_log_section(f"Pushing {args.files}")
    students = cohort.students(args.student or None)
    for student in students:
        student.github_push(files=args.files, subdir=args.subdir, reset=not(args.no_reset), 
                            branch=args.branch or cohort.get("github.branch"), msg=args.message)


if __name__ == "__main__":
    main()
