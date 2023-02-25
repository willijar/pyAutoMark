# Copyright 2023, Dr John A.R. Williams
# SPDX-License-Identifier: GPL-3.0-only
"""Main routine for config command"""

import argparse
from pyam.config import CONFIG, ConfigManager


def add_args(parser: argparse.ArgumentParser) -> None:
    """Add arguments for config command"""
    parser.add_argument(
        'key',
        help="Key of value to be set in '.' format e.g. assessor.username")
    parser.add_argument(
        'value',
        help='value to be set (if no value give output current value)',
        nargs='?',
        default=None)
    parser.add_argument(
        '--type', help="Type conversion to perform on value e.g. int,float")


def main(args=None) -> None:
    """Set or query configuration parameters.

    Keys may be in '.' format e.g. 2022.assessor.username sets assessor.username in cohort 2022
    global name may be used to set global parameters across all cohorts (unless set locally).
    If no value is given print out current value."""
    if args is None:
        parser = argparse.ArgumentParser(description=__doc__)
        add_args(parser)
        args = parser.parse_args()
    components = args.key.split('.')
    domain = components[0]
    remainder = ".".join(components[1:])
    if domain == 'global':
        conf = CONFIG
    else:
        path = CONFIG.cohorts_path / domain
        if not path.exists():
            print(
                f"No configuration found for '{domain}' domain - use a valid cohort name or 'global'"
            )
            return
        conf = ConfigManager(path / "manifest.json", "cohort")
    if args.value is not None:
        conf[remainder] = args.value
        conf.store()
    else:
        print(conf[remainder])


if __name__ == "__main__":
    main()
