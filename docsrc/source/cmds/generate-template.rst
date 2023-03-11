.. _Subcommand generate-template:

generate-template
=================

Synopsis
--------

**pyam generate-template** [-h] [-c COHORT] [-s [STUDENTS [STUDENTS ...]]] [--overwrite] [--prefix PREFIX] [-t TEMPLATE]
                
Description
-----------

:program:`pyam generate-template` Generate a template marking spreadsheet

    Starts from specified template or template-template.xlsx
    and adds in a row per test with the description, a named cell to filled in
    as PASSED or FAILED from the students reports and a mark as per the test
    manifest.

    The following Global defined names are used in template

    * institution_name
    * institution_department
    * course_code
    * course_name
    * assessor_name
    * assessor_email
    * assessment_name
    * automark
    * student_name
    * student_id
    * student_email
    * student_course
    * date
    * mark

    The named cell "automark" marks the start of the section in which the test results will be entered.

Options
-------

.. program:: pyam generate-template

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

   .xlsx file to build template from