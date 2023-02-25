# Copyright 2023, Dr John A.R. Williams
# SPDX-License-Identifier: GPL-3.0-only
"""Standard argumments for sub command scripts

Functions:
  add_common_args(parser): Adds common arguments to parser
"""
import argparse
from typing import Union, List
import pyam.cohort as cohort
from pyam.config import CONFIG



def add_common_args(parser: argparse.ArgumentParser,
                    select: Union[List[str], None] = None) -> None:
    """Add standard arguments to parser"""

    def has(name):
        return not select or name in select

    if has("cohort"):
        parser.add_argument('-c',
                            '--cohort',
                            default=CONFIG.get("cohort",
                                               cohort.current_academic_year()),
                            help="Name of cohort if different from current.")
    if has("students"):
        parser.add_argument(
            '-s',
            '--students',
            nargs="*",
            help='List of specific students to process in cohort.')
    if has("overwrite"):
        parser.add_argument('--overwrite',
                            action="store_true",
                            help="If set overwrite existing output files.")
    if has("prefix"):
        parser.add_argument('--prefix',
                            default="report_",
                            help="Prefix to add to generated files.")
