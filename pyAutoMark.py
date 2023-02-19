#!/usr/bin/env python3
# Copyright 2023, Dr John A.R. Williams
# SPDX-License-Identifier: GPL-3.0-only
"""Automatically retrieve, mark and provide feedback for digital student submissions"""
import argparse
from subprocess import STDOUT, run
import run_tests
import github_retrieve
import extract_downloads
import mark
import generate_template
import find_duplicates
import config
import cohort


def main():
    parser = argparse.ArgumentParser(prog="pyAutoMark",
                                     description=__doc__,
                                     epilog="""
        """)
    #add subparsers for each command
    subparsers = parser.add_subparsers(title="subcommands")
    for command, module,help in (('run', run_tests,"Run automated tests and generate reports"),
                            ('retrieve', github_retrieve,"Retrieve student files from github"),
                            ('extract', extract_downloads,"Extract student files from downloads"),
                            ('mark', mark,"Generate mark spreadsheets from reports and template spreadsheet"),
                            ('generate-template', generate_template, "Generate a template spreadsheet"),
                            ('check-submission', cohort, "Check students have submitted files listed in manifest"),
                            ('find-duplicates', find_duplicates, "Find duplicate students files"),
                            ('config', config, "Set or read configration")):
        sub = subparsers.add_parser(command,help=help)
        module.add_args(sub)
        sub.set_defaults(command=module)
    args = parser.parse_args()
    args.command.main(args)

if __name__ == "__main__":
    main()
