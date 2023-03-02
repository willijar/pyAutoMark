#!/usr/bin/env python3
# Copyright 2023, Dr John A.R. Williams
# SPDX-License-Identifier: GPL-3.0-only
"""Main routine for mark command.
"""

import argparse
from datetime import date
from pathlib import Path
import openpyxl
from pyam.cohort import get_cohort
from pyam.cmd.args import add_common_args
from pyam.cmd.generate_template import to_defined_name

def main(args=None):
    """Generate mark spreadsheets for each student

    Reads in test reports and a template spreadsheet.
    Creates a mark spreadsheet for each student from template
    with the cells named by the test ids set to PASSED or FAILED
    based on the report.

    Completes the following additional defined names in the template for
    each student:

    * student_name
    * student_id
    * student_email
    * student_course
    * date
    * assessor_name
    * course_code
    * course_name
    * course_assessment
    * institution_name
    * institution_department
    """
    if args is None:
        parser = argparse.ArgumentParser(description=__doc__)
        add_args(parser)
        args = parser.parse_args()
    cohort = get_cohort(args.cohort)
    if not args.template:
        args.template = str(cohort.report_path / f"{args.prefix}template.xlsx")
    template = openpyxl.load_workbook(args.template)
    cohort.start_log_section(f"Generating mark sheets from {args.template}")
    students = cohort.students(args.students)
    reports = get_reports(cohort, students, args.reports, args.prefix)
    for student, report in reports.items():
        fill_workbook(template, student, report)
        report_path = cohort.report_path / f"{args.prefix}{student.username}.xlsx"
        if not (args.overwrite) and report_path.exists():
            raise FileExistsError(report_path)
        template.save(report_path)
        cohort.log.info("Generated mark sheet %s.", report_path)


def get_reports(cohort, students, paths, prefix) -> dict:
    """Returns a reports dictionary for given students and reports list"""
    reports = {}
    if paths:
        for path in paths:
            found = False
            for student in students:
                if student.username in str(path) and path.suffix()=="txt":
                    reports[student] = path
                    found = True
                    break
            if not found:
                cohort.log.warning(
                    "Report file %s does not correspond to known student",
                    path)
    else:
        for student in students:
            report = cohort.report_path / f"{prefix}{student.username}.txt"
            if not report.exists():
                cohort.log.warning("No report file found for %s'",
                                   student.name())
            else:
                reports[student] = report
    return reports


def fill_workbook(template, student, report):
    """Fill in workbook 0 of template with student and report details"""
    def set_field(name,value, required=True):
        try:
            for title, coord in template.defined_names[name].destinations:
                    template[title][coord] = value
        except KeyError as e:
            if required:
                print(e)
    cohort = student.cohort
    set_field("student_name",student.name(None))
    set_field("student_id",student.student_id)
    set_field("student_email", f"{student.username}@{cohort.get('institution.domain')}")
    set_field("date",date.today())
    set_field("assessor_name",student.cohort.get("assessor.name"),required=False)
    set_field("course_code",student.cohort.get("course.code"),required=False)
    set_field("course_name",student.cohort.get("course.name"),required=False)
    set_field("course_assessment",student.cohort.get("course.assessment"),required=False)
    set_field("institution_name",student.cohort.get("institution.name"),required=False)
    set_field("institution_department",student.cohort.get("institution.department"),required=False)
    course=student.rec.get("Course")
    if course:
        set_field("student_course",course)

    for key, value in analyse_report(report, cohort.tests(),
                                     cohort.log).items():
        set_field(to_defined_name(key),value)


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
                results[test] = "Unknown"
                log.warning("Missing test result %s in '%s'", test,
                            report_path.name)
    return results


def add_args(parser=argparse.ArgumentParser(description=__doc__)):
    """Add and parse args for this script"""
    add_common_args(parser)
    parser.add_argument(
        '-t',
        '--template',
        type=Path,
        help="Template mark file to use. Defaults to one in cohort directory")
    parser.add_argument(
        '-o',
        '--output',
        type=Path,
        help=
        "Destination path for mark sheets. Defaults to cohort report directory"
    )
    parser.add_argument(
        '--reports',
        nargs=argparse.REMAINDER,
        type=Path,
        default=[],
        help="list of workbooks files to be processed. "
        "Defaults to those in report directory with matching prefix")


if __name__ == "__main__":
    main()
