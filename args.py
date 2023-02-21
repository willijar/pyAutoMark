# Copyright 2023, Dr John A.R. Williams
# SPDX-License-Identifier: GPL-3.0-only
"""Standard argumments for sub command scripts

Functions:
  add_common_args(parser): Adds common arguments to parser
"""
import argparse
import cohort
from config import CONFIG


def add_common_args(parser: argparse.ArgumentParser) -> None:
    """Add standard arguments to parser"""

    parser.add_argument('-c',
                        '--cohort',
                        default=CONFIG.get("cohort",
                                           cohort.current_academic_year()),
                        help="Name of cohort if different from current.")
    parser.add_argument(
        '-s',
        '--students',
        nargs="*",
        help='List of specific students to process in cohort.')
    parser.add_argument('--overwrite',
                        action="store_true",
                        help="If set overwrite existing output files.")
    parser.add_argument('--prefix',
                        default="report_",
                        help="Prefix to add to generated files.")
