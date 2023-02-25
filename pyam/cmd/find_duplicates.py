#!/usr/bin/env python3
# Copyright 2023, Dr John A.R. Williams
# SPDX-License-Identifier: GPL-3.0-only
"""Main routing for find-duplicates command
"""
import argparse
import hashlib
from dataclasses import dataclass
from pathlib import Path
from datetime import datetime
from typing import Sequence, List, Dict
import pyam.cohort as cohort
from pyam.config import CONFIG


@dataclass
class FileRecord:
    """Record of path with student owner, stats and digest

    Attributes:
      student: The Student for this file
      stat: The file.stat for the file
      file: The Path to the file
      digest: The identifying digest of the file
    """
    student: cohort.Student
    file: Path

    def __post_init__(self):
        self.stat = self.file.stat()
        sha = hashlib.sha256()
        blocksize = sha.block_size
        with open(self.file, "rb") as fid:
            block = fid.read(blocksize)
            while block != b"":
                sha.update(block)
                block = fid.read(blocksize)
        self.digest = sha.hexdigest()


def main(args=None):
    """Find duplicate files from students across cohorts"""
    if args is None:
        parser = argparse.ArgumentParser(description=__doc__)
        add_args(parser)
        args = parser.parse_args()
    records = get_records(args.cohorts)
    groups = group_records(records)
    for records in groups.values():
        if len(records) == 1:
            continue
        #Get all unique cohorts
        cohorts = []
        for record in records:
            if record.student.cohort not in cohorts:
                cohorts.append(record.student.cohort)
        msg = f"Duplicate files found."
        for coh in cohorts:
            coh.start_log_section(msg)
        CONFIG.log.warning(msg)
        for record in records:
            msg = f"Duplicate file {record.file.relative_to(CONFIG.root_path)} '{record.student.name()}'"\
            + f" : modified {datetime.fromtimestamp(record.stat.st_mtime)}"
            for coh in cohorts:
                coh.log.warning(msg)
            print(msg)


def get_records(cohort_names: Sequence[str]) -> List[FileRecord]:
    """Given a list of cohort names return a list of FileRecords for each student
       and file in a manifest"""
    records = []
    for name in cohort_names:
        coh = cohort.get_cohort(name)
        files: dict = coh.get("files", ())
        for student in coh.students():
            for file in files.keys():
                filepath = student.path / file[0]
                if filepath.exists():
                    records.append(FileRecord(student=student, file=filepath))
    return records


def group_records(records: List[FileRecord]) -> Dict:
    """GIve a list of file records group them by digest.
    Return a dictionary of matching records indexed by digest"""
    groups = {}
    for record in records:
        key = record.digest
        if key in groups:
            groups[key].append(record)
        else:
            groups[key] = [record]
    return groups


def add_args(parser=argparse.ArgumentParser(description=__doc__)):
    """Add find_duplicates command arguments to parser"""
    parser.add_argument(
        '--cohorts',
        type=str,
        default=[CONFIG.get("cohort", cohort.current_academic_year())],
        nargs=argparse.REMAINDER,
        help="List of cohorts to scan across - defaults to current only")


if __name__ == "__main__":
    main()
