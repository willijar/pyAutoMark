# Copyright 2023, Dr John A.R. Williams
# SPDX-License-Identifier: GPL-3.0-only
"""Implementation of ConfigManager Class

Attributes:

    SCHEMA (dict): A nested dictionary of discriptors for known configuration parameters.
        For each leaf parameter there should be a dictionary with a "description"
        and possibly also a "type"
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Any,Union


class ConfigManager:
    """Base class for entities which have configuration files

    Attributes:
      domain (str): String representing schmea domain
      config_path (Path): The Path to the configuration file
      manifest (dict): The dictionary of loaded configuration parameters
    """

    _global_config = {}

    def __init__(self, config_path: Path, domain: str):
        self.domain: str = domain
        self.config_path: Path = config_path
        self.load()

    def load(self) -> dict:
        """Load configuration from a json file into internal manifest dictionary.

        If file doesn't exist creates a new empty dictionary

        Returns:
            The dictionary of configuration data
        """
        if self.config_path.exists():
            with open(self.config_path, "r") as fid:
                self.manifest = json.load(fid)
        else:
            self.manifest = {}
        return self.manifest

    def store(self) -> None:
        """Store manifest to configuration file, overwriting it."""
        with open(self.config_path, "w") as fid:
            fid.write(json.dumps(self.manifest, indent=2, sort_keys=True))

    @classmethod
    def getconfig(cls, dic: dict, index: str) -> Any:
        """Look up nested dictionaries to retrieve a value

        Args:
            dic (dict): Dictionary
            index (str): index in '.' format e.g. assessor.username

        Raises:
            KeyError: if item not found

        Returns:
            Value at index
        """
        keys = index.split(".")
        for key in keys[:-1]:
            if not isinstance(dic, dict):
                break
            dic = dic[key]
        if isinstance(dic, dict):
            return dic[keys[-1]]
        raise KeyError(f"{index} not found.")

    @classmethod
    def parse_type(cls, value: str, thetype: type):
        """Given a type from schema parse COnfig value using this type

        Class Method

        Args:
            value: The configuration value to be parsed
            thetype: A type to covert value to
        """
        if thetype == datetime:
            return datetime.fromisoformat(value).astimezone()
        elif thetype == Path:
            return Path(value)
        elif thetype == float:
            return float(value)
        else:
            return value

    def __getitem__(self, index: str) -> Any:
        """Implementation of get for ConfigManager TYpes

        See :func:getconfig
        """
        value = ConfigManager.getconfig(self.manifest, index)
        try:
            entry = ConfigManager.getconfig(SCHEMA, index)
            return ConfigManager.parse_type(value, entry.get("type"))
        except KeyError:
            return value

    def __setitem__(self, index: str, newvalue: Any) -> None:
        """Set a configuration item

        Will accept deep indexes in '.' format e.g. assessor.username

        .. warning:
          Does NOT write to configuration file - call store method to do that.
        """
        keys = index.split(".")
        dic = self.manifest
        for key in keys[:-1]:
            if dic.get(key, None) is None:
                dic[key] = {}
            dic = dic[key]
        dic[keys[-1]] = newvalue

    def get(self, index: str, default: Any = []) -> Any:
        """Given a configuration index return a value

        If default is given return that if not in configurations.
        If no default is given loop it up in global config - return None if not found

        Args:
          index: An index (may be in '.' format e.g. assessor.username)
          default: Default value or CONFIG is global dictionary is to be searched as well

        Returns:
          The retrieved value
        """
        try:
            return self[index]
        except KeyError:
            pass
        if default is not self.get.__defaults__[0]:
            return default
        try:
            return ConfigManager._global_config[index]
        except KeyError:
            pass
        try:
            entry = ConfigManager.getconfig(SCHEMA, index)
            return entry["default"]
        except KeyError:
            return None


#Schema - a dictionary of known configuration parameters
SCHEMA = {
    "assessor": {
        "email": {
            "description": "assessor's email address"
        },
        "name": {
            "description": "assessor's name"
        },
    },
    "course": {
        "code": {
            "description": "code for module/course"
        },
        "name": {
            "description": "title for module/course"
        }
    },
    "institution": {
        "name": {
            "description": "name of institution"
        },
        "department": {
            "description": "name of department"
        },
        "domain": {
            "description": "domain to add to usernames for email"
        },
    },
    "github": {
        "url": {
            "description": "url for organisation on github (if applicable)"
        },
        "assignment": {
            "description": "Title of github assignment (prefix for student repositories)",
        },
        "branch": {
            "description":
            "Name of default branch to use in student's repositories",
            "default": "main"
        }
    },
    "fixtures": {
        "description": "List of pytest fixture sets to use",
        "type": list
    },
    "path": {
        "tests": {
            "description": "file path to tests",
            "default": "tests",
            "type": Path
        },
        "build": {
            "description": "file path to build directory for temporary files",
            "default": "build",
            "type": Path
        },
        "cohorts": {
            "description":
            "file path to directory for cohort/student submissions",
            "default": "cohorts",
            "type": Path
        },
        "reports": {
            "description": "file path for reports",
            "default": "reports",
            "type": Path
        },
    },
    "deadline": {
        "description": "deadline for assessment submission",
        "type": datetime
    },
    "student-folder-name": {
        "description": "What field to use for students folder name",
        "default": "username"
    },
    "filematch": {
        "pattern" : {
            "description": "How to match/search for students files - one off exact, glob or regexp.",
            "default": "glob"
        }
    },
    "solution" : {
        "username": { "description": "Username for 'solution' student in cohort"}
    },
    "workbook" : {
        "description": "Name/relative path to students workbook for xlsx fixtures"
    },
    "student-column": {
        "studentid": {
            "description": "The column to read for studentid",
            "default": r"(?i)Student\s*ID"
        },
        "username": {
            "description": "Column to read for students username",
            "default": "(?i)Username"
        },
        "lastname": {
            "description": "Column to read for students last (family) name",
            "default": r"(?i)Last\s*name"
        },
        "firstname": {
            "description": "Column to read for students first (given) name",
            "default": r"(?i)First\s*name"
        },
        "course": {
            "description":
            "Column to read specifying which course student is on (if different from default)",
            "default": "(?i)Child Course ID"
        },
        "github-username": {
            "description":
            "Column to read for the students username on github",
            "default": "(?i)Github Username"
        },
        "submission-date": {
            "description": "Column name to use to record submission dates",
            "default": "Submission Date",
        },
        "extension": {
            "description": "Column name to use for student extensions",
            "default": "Extension"
        }
    },
    "mark-column": {
        "studentid": {
            "description": "Column name in marking csv file with student id",
            "default": "#Cand Key"
        },
        "mark": {
            "description": "Column name in marking csv file for mark",
            "default": "Mark"
        }
    },
    "template": {
        "report": {
            "description" : "Name of cell in marking template for report",
            "default": "report"
        }
    }
}


def write_schema_rst(fid):
    """Write schema out as RST to given file descriptor

    Args:
        fid: A file descriptor to write to
        schema: The schema
    """
    def write_section(section, indent=0):
        prefix = " " * indent
        for key, value in section.items():
            if value.get("description"):  # is terminal node
                if value.get("type"):
                    the_type = f" ({value['type'].__name__})"
                else:
                    the_type = ""
                if value.get("default"):
                    default = f" - default: '{value.get('default')}'"
                else:
                    default = ""
                fid.write(
                    f"{prefix}:{key}:{the_type} {value['description']}{default}\n"
                )
            # determine if
            else:  # new section
                fid.write(f"{prefix}:{key}:\n")
                write_section(value, indent + 4)

    write_section(SCHEMA)
