.. _Subcommand mark:

mark
====

Synopsis
--------

**pyam mark**  [-h] [-c COHORT] [-s [STUDENTS [STUDENTS ...]]] [--overwrite] [--prefix PREFIX] [-t TEMPLATE] [-o OUTPUT]
                [--reports ...]
                
Description
-----------

:program:`pyam mark` generates mark spreadsheets for each student in the reports folder

    Reads in test reports and a template spreadsheet.
    Creates a mark spreadsheet for each student from template
    with the cells named by the test ids set to PASSED or FAILED
    based on the report.

    Completes the following additional defined names in the template for
    each student:

    * student_name
    * student_id
    * student_email
    * student_course
    * date
    * assessor_name
    * course_code
    * course_name
    * course_assessment
    * institution_name
    * institution_department

Options
-------

.. program:: pyam mark

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

.. option:: -t TEMPLATE, --template TEMPLATE

    Template mark file to use. Defaults to one in cohort directory

.. option:: -o OUTPUT, --output OUTPUT
    
    Destination path for mark sheets. Defaults to cohort report directory

.. option:: --reports ...

    List of workbooks files to be processed. Defaults to those in report directory with matching prefix