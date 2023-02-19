# Copyright 2023, Dr John A.R. Williams
# SPDX-License-Identifier: GPL-3.0-only
"""Standard argumments for scripts

Typeical Usage:

  add_common_args(parser)
"""
import argparse
import cohort
from config import CONFIG


def add_common_args(parser: argparse.ArgumentParser) -> None:
    """Add standard arguments to parser"""

    parser.add_argument('-c',
                        '--cohort',
                        default=CONFIG.get("cohort",
                                           cohort.current_cohort_name()),
                        help="Name of student cohort")
    parser.add_argument(
        '-s',
        '--students',
        nargs="*",
        help='Names of specific student for which tests are to be run')
    parser.add_argument('--overwrite',
                        action="store_true",
                        help="If set overwrite existing output files")
    parser.add_argument('--prefix',
                        default="report_",
                        help="Prefix to add to generated files")
