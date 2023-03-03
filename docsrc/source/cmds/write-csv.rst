.. _Subcommand write-csv:

write-csv
=========

Synopsis
--------

**pyam write-csv**  [-h] [-c COHORT] [-s [STUDENTS [STUDENTS ...]]] [--overwrite] [--prefix PREFIX]
                    [--mark-sheets [MARK_SHEETS [MARK_SHEETS ...]]] [--csv-files [CSV_FILES [CSV_FILES ...]]]
                    [--mark-col MARK_COL] [--student-col STUDENT_COL]

Description
-----------

:program:`pyam write-csv` Read marks from a set of mark spreadsheets and write them into csv files


Options
-------

.. program:: pyam write-csv

.. option:: -h, --help

   Show a help message and exit

.. option::  -c COHORT, --cohort COHORT
    
    Name of cohort if different from current.

.. option::  -s [STUDENTS [STUDENTS ...]], --students [STUDENTS [STUDENTS ...]]
    
    List of specific students to process in cohort.

.. option:: --overwrite
    
    If set overwrite existing output files.

.. option:: --prefix PREFIX
    
        Prefix to add to generated files.

.. option:: --mark-sheets [MARK_SHEETS [MARK_SHEETS ...]]

    list of mark sheets to be processed. Defaults to those in report directory with matching prefix

.. option::  --csv-files [CSV_FILES [CSV_FILES ...]]

    List of csv files to be processed. Deafult is those starting with prefix in report directory

.. option:: --mark-col MARK_COL
    
    Name or number of column of csv file where marks are to be written.

.. option:: --student-col STUDENT_COL

    Name or number of student id column in CSV file