#!/usr/bin/env python3
# Copyright 2023, Dr John A.R. Williams
# SPDX-License-Identifier: GPL-3.0-only
"""Run a set of tests for a cohort of students and produce reports files"""
import argparse
import datetime
from subprocess import STDOUT, run
import cohort as cohortlib
import config
from args import add_common_args


def main():
    # pylint: disable=W1510
    args = get_args()
    cohort = cohortlib.get_cohort(args.cohort)
    cohort.start_log_section(
        f"Running tests {args.test} for {args.students or 'all'}")
    students = cohort.student(args.students)
    for student in students:
        report_path = cohort.report_path / f"{args.prefix}{student.username}.txt"
        if report_path.exists():
            if args.new_only:
                continue
            if not args.overwrite:
                raise FileExistsError(report_path)
        extras = []
        if args.mark:
            extras = ['-m', args.mark]
        with open(report_path, "w") as fid:
            fid.write(f"Report generated {datetime.datetime.now().strftime('%Y/%m/%d %H:%M')}"\
                      + f" for {student.name()} by {cohort.manifest['assessor']['name']}\n")
            fid.flush()
            result = run([
                "pytest", '--no-header', '-rA', '--tb=short', '-v', *extras,
                '--student', student.username, '--cohort', args.cohort
            ],
                         stdout=fid,
                         stderr=STDOUT,
                         cwd=cohort.test_path)
        if result.returncode == 0:
            cohort.log.info("Passed all tests : '%s' - report '%s'.",
                            student.name(),
                            report_path.relative_to(config.ROOT_PATH))
        else:
            cohort.log.warning("Failed test: '%s' - report '%s'.",
                               student.name(),
                               report_path.relative_to(config.ROOT_PATH))


def get_args(parser=argparse.ArgumentParser(description=__doc__)):
    """Parse Args and return them for this script"""
    add_common_args(parser)
    parser.add_argument('-t',
                        '--test',
                        default="",
                        help="Name of specific test to be run")
    parser.add_argument(
        '--new_only',
        action="store_true",
        help=
        "If set then only run tests for those student for whom there are no reports"
    )
    parser.add_argument(
        '-m',
        '--mark',
        help=
        "Selected mark tests when testing e.g. 'no slow' to not run slow tests"
    )
    return parser.parse_args()


if __name__ == "__main__":
    main()
