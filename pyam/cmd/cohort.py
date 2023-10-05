# Copyright 2023, Dr John A.R. Williams
# SPDX-License-Identifier: GPL-3.0-only
"""Main routine for pyAutoMark cohort command"""

import argparse
from datetime import datetime
from pyam.config import CONFIG
from pyam.cohort import get_cohort, current_academic_year, list_cohorts


# pylint: disable=W0613
def main(args=None):
    """Set or query cohort information.

    If no cohort is specified list all valid cohorts.
    If given a cohort name but no further command set the default cohort.
    """
    if args.cohort:
        cohort = get_cohort(args.cohort)
        CONFIG["cohort"] = args.cohort
        CONFIG.store()
    else:
        cohort = get_cohort(CONFIG.get("cohort", current_academic_year()))
    if args.list_students:
        today = datetime.today().astimezone()
        deadline = cohort.get("deadline", None)
        print(f"Deadline: {deadline}")
        print("-" * 100)
        print(f"{'Student':40} | {'Submission Date':40} | Lateness")
        print("-" * 100)
        for student in cohort.students():
            if not student.path.exists():
                print(f"{student.name():40} | No submission")
                continue
            submission_time = student.rec.get("submission-date", None)
            if submission_time:
                submission_time = datetime.fromisoformat(submission_time).astimezone()
                days_ago = (today - submission_time).days
                days_ago = f"{days_ago:3} days ago. |"
                extension= student.rec.get("extension", None)
                if extension:
                    student_deadline=datetime.fromisoformat(extension).astimezone()
                else:
                    student_deadline=deadline
                past_deadline = ""
                if deadline:
                    diff = (submission_time - student_deadline)
                    if diff.days > 0:
                        past_deadline = f"Late {diff.days} days"
                if extension:
                    extension=f"(Extension: {extension})"
                print(
                    f"{student.name():40} | {submission_time.strftime('%c')} - {days_ago:15} {past_deadline} {extension}"
                )
            else:
                print(f"{student.name():40} | Unknown {' ':32} |")
        print("-" * 100)
    elif args.list_files:
        for file, value in cohort["files"].items():
            print(f"{file:30}: {value['description']}")
    elif args.list_tests:
        for test in cohort.tests().keys():
            print(f"{test:40}: {cohort.tests()[test]}")
    elif args.list_hashes:
        for student in sorted(cohort.students(),key=lambda s: s.username):
            print(f"{student.username:10} | {hex(student.hash())}")
    elif args.check_submissions:
        cohort.start_log_section("Checking Student Submissions")
        for student in cohort.students():
            student.check_manifest(log=True)
    else:
        for name in list_cohorts():
            if name == CONFIG.get("cohort"):
                name += " <-"
            print(name)


def add_args(parser: argparse.ArgumentParser):
    """Add args for this command - none"""
    parser.add_argument(dest="cohort",
                        nargs="?",
                        default=None,
                        help="Name of cohort to set as default or query")
    parser.add_argument('--list-students',
                        action="store_true",
                        help="Print out student details (from students.csv)")
    parser.add_argument('--list-files',
                        action="store_true",
                        help="Print out file manifest (from manifest.json)")
    parser.add_argument('--list-hashes',
                        action="store_true",
                        help="Print hexadecimal hash for each student id")
    parser.add_argument(
        '--check-submissions',
        action="store_true",
        help="Check student submissions listing missing files for each student."
    )
    parser.add_argument(
        '--list-tests',
        action="store_true",
        help=
        "Print out test information - either from test manifest or pytest collect"
    )


if __name__ == "__main__":
    main()
