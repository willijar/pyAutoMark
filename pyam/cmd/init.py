# Copyright 2023, Dr John A.R. Williams
# SPDX-License-Identifier: GPL-3.0-only
"""Main routine for pyAutoMark init command"""

import sys
import argparse
from pathlib import Path
import pyam.config_manager as conf

PATH_PARAMETERS = ("path.cohorts", "path.tests", "path.reports", "path.build")

INIT_PARAMETERS = (*PATH_PARAMETERS, "institution.name",
                   "institution.department", "institution.domain",
                   "assessor.name", "assessor.email", "course.code",
                   "course.name", "github.url")


def main(args=None):
    """Initialise a directory for pyAutoMark

    Creates configuration pyAutoMark.json and subdirectories
    based on a few questions
    """
    if args is None:
        parser = argparse.ArgumentParser(description=__doc__)
        add_args(parser)
        args = parser.parse_args()
    root_path = args.path.expanduser().resolve()
    config = conf.ConfigManager(root_path / "pyAutoMark.json", "global")
    print("Initialising pyAutoMark in ", root_path)
    values = {}
    for item in INIT_PARAMETERS:
        while True:
            schema = conf.ConfigManager.getconfig(conf.SCHEMA, item)
            default = config.get(item, schema.get("default", ""))
            description = schema["description"]
            typeconv = schema.get("type", str)
            value = term_input(
                f"Enter {description}. Default value [{default}]: ")
            values[item] = value
            if not value or value == default:
                break
            try:
                value = typeconv(value)
                if typeconv == Path:
                    value = str(
                        (root_path /
                         value).expanduser().resolve().relative_to(root_path))
                    print(value)
                config[item] = value
                break
            except ValueError as excep:
                print(excep)
                continue
    print("Saving configuration file ", config.config_path)
    config.store()
    for param in PATH_PARAMETERS:
        schema = conf.ConfigManager.getconfig(conf.SCHEMA, param)
        default = config.get(param, schema.get("default", ""))
        value = values[param] or default
        value = (root_path / value).resolve()
        if not value.exists():
            description = schema["description"]
            print("Creating", description, value)
            value.mkdir()


# function to get input from terminal -- overridden by the test suite
def term_input(prompt: str) -> str:
    """Function to get input from terminal - even windows"""
    if sys.platform == 'win32':
        print(prompt, end='')
        return input('')
    return input(prompt).strip()


def add_args(parser: argparse.ArgumentParser):
    """Add args for this command - none"""
    parser.add_argument(dest='cmd', nargs=1, help="Command - mut be init")
    parser.add_argument(nargs="?",
                        dest="path",
                        default=Path("./"),
                        type=Path,
                        help="Directory to initialise - default is current")


if __name__ == "__main__":
    main()
