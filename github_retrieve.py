#!/usr/bin/env python3
# Copyright 2023, Dr John A.R. Williams
# SPDX-License-Identifier: GPL-3.0-only
"""Retrieve student files from github"""
import argparse
from args import add_common_args
from cohort import get_cohort

#import importlib

# def import_py(self,module_name):
#     spec = importlib.util.spec_from_file_location(module_name, self.path(module_name+".py"))
#     module = importlib.util.module_from_spec(spec)
#     spec.loader.exec_module(module)


def get_args(parser=argparse.ArgumentParser(description=__doc__)):
    "Parse and return args for this script"
    add_common_args(parser)
    return parser.parse_args()


def main():
    args = get_args()
    cohort = get_cohort(args.cohort)
    cohort.start_log_section(f"Github retrieve {args.students or 'all'}")
    students = cohort.student(args.students)
    for student in students:
        student.github_retrieve()


if __name__ == "__main__":
    main()
