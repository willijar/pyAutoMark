#!/usr/bin/env python3
# Copyright 2023, Dr John A.R. Williams
# SPDX-License-Identifier: GPL-3.0-only
"""Extracts files for given list of archive files into student directories under cohort"""

import shutil
import re
import argparse
from pathlib import Path
from datetime import datetime
import pyam.cohort
from pyam.args import add_common_args
import pyam.files


def add_args(parser):
    """Get and parse arguments for this script"""
    add_common_args(parser)
    parser.add_argument('--files',
                        dest="files",
                        nargs=argparse.REMAINDER,
                        type=Path,
                        default=[],
                        help="list of workbooks files to be processed")

_gradecentre_re=re.compile(".+_(.+?)_attempt_(.+?)[_.](.+)")


def extract_details(file,log=None):
    match=_gradecentre_re.match(str(file))
    if match:
        return(match.group(1), # username
                match.group(3), # filename or txt
                datetime.strptime(match.group(2), "%Y-%m-%d-%H-%M-%S")) # date


def main(args=None):
    """Extract the files"""
    if args is None:
        parser=argparse.ArgumentParser(description=__doc__)
        add_args(parser)
        args=parser.parse_args()
    cohort = pyam.cohort.get_cohort(args.cohort)
    cohort.path.mkdir(exist_ok=True)
    cohort.start_log_section(f"Extracting downloads for Cohort {args.cohort}")
    students = list(cohort.students)
    submission_dates={}
    for file in args.files:
        (username,filename,date)=extract_details(file)
        if not username:
            cohort.log.warning("Unrecognised download file %s", file)
            continue
        try:
            student = cohort.student(username)
        except KeyError:
            cohort.log.warning("Download file from %s who is not student in cohort",username)
            continue
        if filename=="txt": # this is the download details txt - copy to student directory
            shutil.copy2(file,student.path)
        else:
            try:
                shutil.unpack_archive(file, student.path)
                cohort.log.info("Extracted files for %s from %s", student.username, file.name)
            except ValueError: # not recognised archive format
                shutil.copy2(file,student.path / filename)
                cohort.log.info("Copied %s to %s", file.name, student.path / filename)
            submission_dates[username]=date
            if student in students:
                students.remove(student)
    pyam.files.set_csv_column(cohort.path / "students.csv","Submission Date","Username",lambda x: submission_dates.get(x,None))
    for student in cohort.students:
        if student not in students:
            student.check_manifest(log=True)
        else: 
            cohort.log.warning("No download found for student %s", student)


if __name__ == "__main__":
    main()
