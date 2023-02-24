# Copyright 2023, Dr John A.R. Williams
# SPDX-License-Identifier: GPL-3.0-only
"""Various file searching utilities for the tests"""
import shutil
import os
from pathlib import Path
import csv


def get_depends(name,depends):
    results=[]
    for item in depends:
        if item[0]==name:
            for i in item[1:]:
                for item in get_depends(i,depends):
                    if not item in results: results.append(item)
            break
    results.append(name)
    return results

def find_executable(name,paths):
    exec=shutil.which(name)
    if exec: return Path(exec)
    for path in paths:
        for match in Path(path).glob(f"**/{name}"):
            if os.path.isfile(match) and os.access(match, os.X_OK):
                return match
    raise FileNotFoundError(f"Executable {name} not found")

def read_csv(filename, columns=[]):
    """Read a csv file.
    If columns is a list - return as dictionary using these as column names
    Else if columns is true use first line as column names.
    Else return just as list of lists"""
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

def set_csv_column(filename,column_name,key_name,get_value):
    """Reads through a csv file overwriting specific named columns
    
    Args:
      filename: files to csv file
      column_name: name of column name to be written to
      key_name: name of column to use as key
      get_value: a function which, given a key returns a new value
               if it returns None old value is kept
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

