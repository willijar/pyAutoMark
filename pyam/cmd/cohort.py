# Copyright 2023, Dr John A.R. Williams
# SPDX-License-Identifier: GPL-3.0-only
"""Support functions for assessing students and running tests by cohort

Classes:
  Cohort: representing a specific cohort
  Student: representing a student in a cohort

Functions:
  get_cohort:
    Gets a cohort by name (or default cohort)
  current_academic_year:
    returns a generated default cohort name by current (UK style) academic year
"""

import argparse
from datetime import datetime
from pyam.config import CONFIG
from pyam.cohort import get_cohort, current_academic_year, list_cohorts


# pylint: disable=W0613
def main(args=None):
    """Main routine - checks student manifest in a cohort"""
    cohort=get_cohort(CONFIG.get("cohort", current_academic_year()))
    if args.list_students:
        today=datetime.today().astimezone()
        deadline=cohort.get("deadline",None)
        if deadline:
            deadline=datetime.fromisoformat(deadline).astimezone()
        print(f"Deadline: {deadline}")
        for student in cohort.students():
            if not student.path.exists():
                print(f"{student.name():40}: No submission")
                continue
            submission_time=student.rec.get("Submission Date",None)
            if submission_time:
                submission_time=datetime.fromisoformat(submission_time)
                days_ago=(today-submission_time).days
                days_ago=f"{days_ago:3} days ago."
                past_deadline=""
                if deadline:
                    past_deadline=(submission_time-deadline)
                    if past_deadline.days>0:
                        past_deadline=f"Late {past_deadline.days} days"
                print(f"{student.name():40}: {submission_time.strftime('%c')}: {days_ago:15} {past_deadline}")
            else:
                print(f"{student.name():40}: Unknown Submission Time")
    elif args.list_files:
        for file,value in cohort["files"].items():
            print(f"{file:30}: {value['description']}")
    elif args.list_tests:
        for test in cohort.tests().keys():
            print(test)
    elif args.cohort:
        get_cohort(args.cohort)
        CONFIG["cohort"]=args.cohort
        CONFIG.store()
        print("Default cohort is now: ", CONFIG["cohort"])
    else:
        for name in list_cohorts():
            if name==CONFIG.get("cohort"):
                name+=" <-"
            print(name)

def add_args(parser: argparse.ArgumentParser):
    """Add args for this command - none"""
    parser.add_argument(
        dest="cohort", nargs="?", default=None,
        help="Name of cohort to set as default"
    )
    parser.add_argument(
        '--list-students', action="store_true",
        help="If set print out student details in current cohort"
    )
    parser.add_argument(
        '--list-files', action="store_true",
        help="If set print out student details in current cohort"
    )
    parser.add_argument(
        '--list-tests', action="store_true",
        help="If set print out student details in current cohort"
    )


if __name__ == "__main__":
    main()
