#!/usr/bin/env python3
# Copyright 2023, Dr John A.R. Williams
# SPDX-License-Identifier: GPL-3.0-only
"""Main generate-template command.
"""
import argparse
from pathlib import Path
import openpyxl
from openpyxl.workbook.defined_name import DefinedName
from openpyxl.utils import quote_sheetname, absolute_coordinate
from pyam.config import CONFIG
from pyam.cmd.args import add_common_args
from pyam.cohort import get_cohort
import re

def to_defined_name(nodeid: str) -> str:
    """Convert a test nodeid into a format suitable for xlsx defined name

    Args:
        nodeid (str): The Nodeid

    Returns:
        str: A valid XLSX defined name
    """
    return re.sub("[^a-zA-Z0-9_]+","_",nodeid)

def main(args=None):
    """Generate a template marking spreadsheet

    Starts from specified template or template_template.xlsx
    and adds in a row per test with the description, a named cell to filled in
    as PASSED or FAILED from the students reports and a mark as per the test
    manifest.

    The following Global defined names are used in template

    institution_name
    institution_department
    course_code
    course_name
    assessor_name
    assessor_email
    assessment_name
    automark
    student_name
    student_id
    student_email
    student_course
    date
    mark
    """
    if args is None:
        parser = argparse.ArgumentParser(description=__doc__)
        add_args(parser)
        args = parser.parse_args()
    cohort = get_cohort(args.cohort)
    destination = cohort.report_path / f"{args.prefix or cohort.get('template.prefix')}_template.xlsx"
    if not (args.overwrite) and destination.exists():
        raise FileExistsError(destination)
    cohort.start_log_section(
        f"Generate template {destination.relative_to(CONFIG.root_path)}")
    template = openpyxl.load_workbook(args.template)
    for field in ("institution.name",  "institution.department", "course.code", "course.name",
                  "assessor.name", "assessor.email", "assessment.name"):
        try:
            for title, coord in template.defined_names[field.replace('.','_')].destinations:
                template[title][coord] = cohort.get(field)
        except KeyError:
            #ignore if not present
            pass
    # find start point for marks - will use worksheet[0]["B14"] if none provided
    worksheet=template.worksheets[0]
    coord=cohort.get("template.marking-cell-ref")
    for title,dest_coord in template.defined_names["automark"].destinations:
        worksheet=template[title]
        coord=dest_coord
        break # finish after first
    start_cell=worksheet[coord]
    column=start_cell.column_letter
    row=0
    mapping=cohort.get("template.mapping",{})
    items=cohort.tests().items()
    if args.sorted:
        items=sorted(items,key=lambda a: a[1].get("description",a[0]))
    for test, details in items:
        start_cell.offset(row,0).value=details.get("description", test)
        cell=start_cell.offset(row,1)
        cell.value=mapping.get("UNKNOWN","UNKNOWN")
        ref = f"{quote_sheetname(worksheet.title)}!{absolute_coordinate(f'{cell.coordinate}')}"
        defn = DefinedName(name=details.get("cell",to_defined_name(test)), attr_text=ref)
        template.defined_names.add(defn)
        mark=details.get("mark",None)
        if mark is not None:
            start_cell.offset(row,2).value=mark
        row += 1
    worksheet.delete_rows(row+14,99)
    template.save(destination)


def add_args(parser=argparse.ArgumentParser(description=__doc__)):
    """Return args for this script"""
    add_common_args(parser)
    parser.add_argument(
        "-t","--template", type=Path, default=Path(__file__).parent.parent / "template-template.xlsx",
        help=".xlsx file to build template from"
    )
    parser.add_argument(
        "--sorted",
        action="store_true",
        help="If set items will be in sorted order"
    )



if __name__ == "__main__":
    main()
