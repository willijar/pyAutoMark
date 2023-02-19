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


def main():
    parser = argparse.ArgumentParser(prog="pyAutoMark",
                                     description=__doc__,
                                     epilog="""
        """)
    #add subparsers for each command
    subparsers = parser.add_subparsers(title="subcommands")
    for command, module in (('run', run_tests),
                            ('retrieve', github_retrieve),
                            ('extract', extract_downloads),
                            ('mark', mark),
                            ('generate-template', generate_template),
                            ('find-duplicates', find_duplicates)):
        sub = subparsers.add_parser(command)
        sub.set_defaults(command=module)
        module.add_args(sub)
    #execute main from selected module
    args = parser.parse_args()
    args.command.main(args)

if __name__ == "__main__":
    main()
