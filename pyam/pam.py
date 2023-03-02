#!/usr/bin/env python3
# Copyright 2023, Dr John A.R. Williams
# SPDX-License-Identifier: GPL-3.0-only
"""Automatically retrieve, mark and provide feedback for digital student submissions"""
import argparse
import sys
import pyam.cmd.init

# need to test for init command before config is imported for other commands
if len(sys.argv)>=1 and sys.argv[1]=="init":
    pyam.cmd.init.main()
    quit()

import pyam.cmd.run
import pyam.cmd.github_retrieve
import pyam.cmd.extract_downloads
import pyam.cmd.mark
import pyam.cmd.generate_template
import pyam.cmd.find_duplicates
import pyam.cmd.config
import pyam.cmd.cohort
import pyam.cmd.write_csv

def main():
    """Automatically retrieve, mark and provide feedback for digital student submissions"""
    parser = argparse.ArgumentParser(prog="pyAutoMark",
                                     description=__doc__,
                                     epilog="""
        """)
    #add subparsers for each command
    subparsers = parser.add_subparsers(title="subcommands")
    for command, module in (
            ('run', pyam.cmd.run),
            ('retrieve', pyam.cmd.github_retrieve),
            ('extract', pyam.cmd.extract_downloads),
            ('mark', pyam.cmd.mark),
            ('generate-template', pyam.cmd.generate_template),
            ('find-duplicates', pyam.cmd.find_duplicates),
            ('config', pyam.cmd.config),
            ('cohort', pyam.cmd.cohort),
            ('write-csv', pyam.cmd.write_csv),
            ('init', pyam.cmd.init)):
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
