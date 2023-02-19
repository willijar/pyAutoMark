#!/usr/bin/env python3
# Copyright 2023, Dr John A.R. Williams
# SPDX-License-Identifier: GPL-3.0-only
"""Retrieve student files from github"""
import argparse
from args import add_common_args
from cohort import get_cohort

def add_args(parser=argparse.ArgumentParser(description=__doc__)):
    "Parse and return args for this script"
    add_common_args(parser)

def main(args=None):
    if args is None:
        parser=argparse.ArgumentParser(description=__doc__)
        add_args(parser)
        args=parser.parse_args()
    cohort = get_cohort(args.cohort)
    cohort.start_log_section(f"Github retrieve {args.students or 'all'}")
    students = cohort.student(args.students)
    for student in students:
        student.github_retrieve()


if __name__ == "__main__":
    main()
