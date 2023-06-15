# Copyright 2023, Dr John A.R. Williams
# SPDX-License-Identifier: GPL-3.0-only
"""Various file searching utilities for the tests"""
import shutil
import os
import re
import argparse
from pathlib import Path
from typing import Any, Union, List, Dict, Callable
import csv

class PathGlob(argparse.Action):
    """File Glob Action aimed to works for Windows and Linux
    
    On Windows it treats every value as a potential glob expression to be expanded
    and adds the results onto the stored values.

    On other systems the shell will already have expanded the expressions so just treat as a path

    """

    def __call__(self, parser, namespace, values, option_string=None):
        items = getattr(namespace, self.dest) or []
        for item in values:
            if os.name=='nt':
                items.extend(Path().glob(item))
            else:
                items.append(Path(item))
            setattr(namespace, self.dest, items)



def expand_files(filearg):
    """Given a files value (from args.files) expand the list using glob
    
    This is needed as Windows OS does not expand the file globs before passing to programmes"""
    if os.name=='nt':
        files=[]
        for file in filearg:
            files += Path().rglob(file)
    else:
        files=[Path(filearg)]
    return files

def get_depends(name: Any, depends: List[List]) -> List[Any]:
    """Determine the dependencies for a particular (file) name from a
    dependency graph. Recurses the depends graph, will return dependencies in order.

    Args:
        name (Any): Item for which dependencies
        depends (List[List]): A recursive dependency graph

    Returns:
        The ordered list of dependencies for name
    """
    results = []
    for item in depends:
        if item[0] == name:
            for i in item[1:]:
                for elem in get_depends(i, depends):
                    if not elem in results:
                        results.append(elem)
            break
    results.append(name)
    return results


def find_executable(name: str, paths: List[Union[Path, str]]) -> Path:
    """Find path to an executable program.

    This will return full path from the system PATH. If not found there
    it will search the given list of directories (recursively) until it finds
    an executable with given name.

    Args:
        name: Name of program to be found
        paths: List of additional paths to search

    Raises:
        FileNotFoundError: If no suct executable found

    Returns:
        Path to executable
    """

    executable = shutil.which(name)
    if executable:
        return Path(executable)
    for path in paths:
        for match in Path(path).glob(f"**/{name}"):
            if os.path.isfile(match) and os.access(match, os.X_OK):
                return match
    raise FileNotFoundError(f"Executable {name} not found")


def read_csv(filename: Union[Path, str],
             columns: Union[List, bool] = []) -> List[Dict[str, str]]:
    """Read a csv file.

    .. warning::
        The return type of this may change to a NamedTuple in future

    Args:
        filename: csv file to read
        columns: A list of tuples of regex's to match against csv titles and column names,
          or if True read column names from first line.

    Returns:
      * If columns is a list - use these to remap names.
      * Else if columns is true use first line as column names.
      * Else return just as list of lists
    """
    rows = []
    with open(filename, 'r', encoding="utf-8-sig") as fid:
        reader = csv.reader(fid, delimiter=',', quotechar='"')
        for row in reader:
            rows.append(row)
    if columns == read_csv.__defaults__[0]:
        return rows
    if columns == True:
        headers = rows[0]
    else:
        headers = []
        for header in rows[0]:
            for col in columns:
                if re.match(col[0], header):
                    headers.append(col[1])
                    break
            else:
                headers.append(header)
    result = []
    for row in rows[1:]:
        record = {}
        for field, value in zip(headers, row):
            record[field] = value
        result.append(record)
    return result


def set_csv_column(filename: Union[Path, str], column_name: str, key_name: str,
                   get_value: Callable[[str], str]):
    """Reads through a csv file overwriting specific named columns

    Args:
      filename: path to the csv file
      column_name: name or regex matching column name to be written to
      key_name: name or regex matching column to use as key
      get_value: a function which, given a key returns a new value
               if it returns None old value is kept.
    """
    rows = []
    with open(filename, 'r', encoding="utf-8-sig") as fid:
        reader = csv.reader(fid, delimiter=',', quotechar='"')
        coltitles = reader.__next__()
        try:
            dest = coltitles.index(column_name)
        except ValueError:
            dest = len(coltitles)
            coltitles.append(column_name)
        key_col = coltitles.index(key_name)
        for row in reader:
            value = get_value(row[key_col])
            if value is not None:
                if dest == len(row):
                    row.append(value)
                else:
                    row[dest] = value
            rows.append(row)
    with open(filename, 'w', newline='') as fid:
        writer = csv.writer(fid, delimiter=',', quotechar='"')
        writer.writerow(coltitles)
        for row in rows:
            writer.writerow(row)
