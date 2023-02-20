#!/usr/bin/env python3
# Copyright 2023, Dr John A.R. Williams
# SPDX-License-Identifier: GPL-3.0-only
"""Generate mark spreadsheets for each student

Reads in test reports and a template spreadsheet
Creates a mark spreadsheet for each student from template
with the cells named by the test ids set to PASSED or FAILED
based on the report.

Typical Usage:

mark.py --cohort 2022
"""

import argparse
from datetime import date
from pathlib import Path
import openpyxl
from cohort import get_cohort
from args import add_common_args


def main(args=None):
    """Iterate through student reports to generate mark spreadhseets from template spreadsheet"""
    if args is None:
        parser = argparse.ArgumentParser(description=__doc__)
        add_args(parser)
        args = parser.parse_args()
    cohort = get_cohort(args.cohort)
    if not args.template:
        args.template = str(cohort.report_path / "template.xlsx")
    template = openpyxl.load_workbook(args.template)
    cohort.start_log_section(f"Generating mark sheets from {args.template}")
    students = cohort.student(args.students)
    if args.reports:
        reports = {}
        for path in args.reports:
            found = False
            for student in students:
                if student.username in str(path):
                    reports[student] = path
                    found = True
                    break
            if not found:
                cohort.log.warning(
                    "Report file %s does not correspond to known student",
                    path)
        args.reports = reports
    else:
        args.reports = {}
        for student in students:
            report = cohort.report_path / f"{args.prefix}{student.username}.txt"
            if not report.exists():
                cohort.log.warning("No report file found for %s'",
                                   student.name())
            else:
                args.reports[student] = report
    for student, report in args.reports.items():
        workbook = template.worksheets[0]
        workbook["B4"] = student.name()
        workbook["B5"] = student.student_id
        workbook["B6"] = student.username + cohort.get("domain")
        workbook["B8"] = cohort.get('assessor.name')
        workbook["B9"] = cohort.get('assessor.email')
        workbook["B10"] = str(date.today())
        for key, value in analyse_report(report, cohort.tests(),
                                         cohort.log).items():
            for title, coord in template.defined_names[key].destinations:
                template[title][coord] = value
        report_path = cohort.report_path / f"{args.prefix}{student.username}.xlsx"
        if not (args.overwrite) and report_path.exists():
            raise FileExistsError(report_path)
        template.save(report_path)
        cohort.log.info("Generated mark sheet %s.", report_path)


def analyse_report(report_path: Path, tests: dict, log=None):
    """Returns a dictionary of results from a report file at path"""
    results = {}
    with open(report_path, 'r') as fid:
        for line in fid.readlines():
            if "PASSED" in line:
                result = "PASSED"
            elif "FAILED" in line:
                result = "FAILED"
            else:
                continue
            for test in tests.keys():
                if test in line:
                    results[test] = result
    if log:
        #check we have all expected results in report
        for test in tests.keys():
            if test not in results:
                log.warn("Missing test result %s in report %s", test,
                         report_path)
    return results


def add_args(parser=argparse.ArgumentParser(description=__doc__)):
    """Add and parse args for this script"""
    add_common_args(parser)
    parser.add_argument('-t',
                        '--template',
                        type=Path,
                        help="Template mark file")
    parser.add_argument('-o',
                        '--output',
                        type=Path,
                        help="Destination path for mark sheets")
    parser.add_argument('--reports',
                        nargs=argparse.REMAINDER,
                        type=Path,
                        default=[],
                        help="list of workbooks files to be processed")


if __name__ == "__main__":
    main()
