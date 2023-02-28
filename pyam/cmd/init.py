# Copyright 2023, Dr John A.R. Williams
# SPDX-License-Identifier: GPL-3.0-only
"""Main routine for pyAutoMark init command"""

import argparse
from pathlib import Path


# pylint: disable=W0613
def main(args=None):
    """Initialise a directory for pyAutoMark

    Creates configuration pyAutoMark.json and subdirectories
    based on a few questions
    """
    if args is None:
        parser = argparse.ArgumentParser(description=__doc__)
        add_args(parser)
        args = parser.parse_args()

    print("Path=",args.path)



def add_args(parser: argparse.ArgumentParser):
    """Add args for this command - none"""
    parser.add_argument(dest='cmd', nargs=1, 
                        help="Command - mut be init")
    parser.add_argument('--path', default=Path("./"), type = Path,
                        help="Directory to initialise - default is current")



if __name__ == "__main__":
    main()
