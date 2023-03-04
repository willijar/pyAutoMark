# Copyright 2023, Dr John A.R. Williams
# SPDX-License-Identifier: GPL-3.0-only
"""Various file searching utilities for the tests"""
import shutil
import os
from pathlib import Path
from typing import Any,Union,List,Dict,Callable
import csv


def get_depends(name: Any,depends: List[List]) -> List[Any]:
    """Determine the dependencies for a particular (file) name from a
    dependency graph. Recurses the depends graph, will return dependencies in order.

    Args:
        name (Any): Item for which dependencies
        depends (List[List]): A recursive dependency graph

    Returns:
        The ordered list of dependencies for name
    """
    results=[]
    for item in depends:
        if item[0]==name:
            for i in item[1:]:
                for item in get_depends(i,depends):
                    if not item in results: results.append(item)
            break
    results.append(name)
    return results

def find_executable(name: str,paths: List[Union[Path,str]]) -> Path:
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

    exec=shutil.which(name)
    if exec: return Path(exec)
    for path in paths:
        for match in Path(path).glob(f"**/{name}"):
            if os.path.isfile(match) and os.access(match, os.X_OK):
                return match
    raise FileNotFoundError(f"Executable {name} not found")

def read_csv(filename: Union[Path,str], columns: Union[List,bool]=[]) -> List[Dict[str,str]]:
    """Read a csv file.
    
    .. warning::
        The return type of this may change to a NamedTuple in future

    Args:
        filename: csv file to read
        columns: A list of column names, or if True read column names from first line.

    Returns:
      * If columns is a list - return as dictionary using these as column names
      * Else if columns is true use first line as column names.
      * Else return just as list of lists
    """
    rows=[]
    with open(filename,'r') as fid:
        reader=csv.reader(fid, delimiter=',',quotechar='"')
        for row in reader:
            rows.append(row)
    if columns == read_csv.__defaults__[0]:
        return rows
    if columns == True:
        columns = rows[0]
        rows = rows[1:]
    result = []
    for row in rows:
        record = {}
        for field, value in zip(columns, row):
            record[field] = value
        result.append(record)
    return result

def set_csv_column(filename: Union[Path,str], column_name: str, key_name: str, get_value: Callable[[str],str]):
    """Reads through a csv file overwriting specific named columns
    
    Args:
      filename: path to the csv file
      column_name: name of column name to be written to
      key_name: name of column to use as key
      get_value: a function which, given a key returns a new value
               if it returns None old value is kept.
    """
    rows=[]
    with open(filename,'r') as fid:
        reader=csv.reader(fid, delimiter=',',quotechar='"')
        coltitles=reader.__next__()
        try:
            dest=coltitles.index(column_name)
        except ValueError:
            dest=len(coltitles)
            coltitles.append(column_name)
        key_col=coltitles.index(key_name)
        for row in reader:
            value=get_value(row[key_col])
            if value is not None:
                if dest==len(row):
                    row.append(value)
                else:
                    row[dest]=value
            rows.append(row)
    with open(filename,'w') as fid:
        writer=csv.writer(fid,delimiter=',',quotechar='"')
        writer.writerow(coltitles)
        for row in rows:
            writer.writerow(row)

