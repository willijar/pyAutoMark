#!/usr/bin/env python3
# Copyright 2023, Dr John A.R. Williams
# SPDX-License-Identifier: GPL-3.0-only
"""Automatically retrieve, mark and provide feedback for digital student submissions"""
import argparse
import pyam.run_tests
import pyam.github_retrieve
import pyam.extract_downloads
import pyam.mark
import pyam.generate_template
import pyam.find_duplicates
import pyam.config
import pyam.cmd.cohort


def main():
    """Automatically retrieve, mark and provide feedback for digital student submissions"""
    parser = argparse.ArgumentParser(prog="pyAutoMark",
                                     description=__doc__,
                                     epilog="""
        """)
    #add subparsers for each command
    subparsers = parser.add_subparsers(title="subcommands")
    for command, module, doc in (
            ('run', pyam.run_tests, "Run automated tests and generate reports"),
            ('retrieve', pyam.github_retrieve, "Retrieve student files from github"),
            ('extract', pyam.extract_downloads, "Extract student files from downloads"),
            ('mark', pyam.mark, "Generate mark spreadsheets from reports and template spreadsheet"),
            ('generate-template', pyam.generate_template, "Generate a template spreadsheet"),
            ('check-submission', pyam.cmd.cohort, "Check students have submitted files listed in manifest"),
            ('find-duplicates', pyam.find_duplicates, "Find duplicate students files"),
            ('config', pyam.config, "Set or read configration"),
            ('cohort', pyam.cohort, "Set default cohort, query cohort")):
        description=module.main.__doc__
        doc=description.splitlines()[0]
        sub = subparsers.add_parser(
            command,
            description=description,
            help=doc,
            formatter_class=argparse.RawDescriptionHelpFormatter)
        module.add_args(sub)
        sub.set_defaults(command=module)
    args = parser.parse_args()
    args.command.main(args)


if __name__ == "__main__":
    main()
