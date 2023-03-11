.. _Subcommand cohort:

cohort
======

Synopsis
--------

**pyam cohort**  [-h] [--list-students] [--list-files] [--check-submissions] [--list-tests] [cohort]
                
Description
-----------

:program:`pyam cohort` Set or query cohort information.

    If no cohort is specified list all valid cohorts.
    If given a cohort name but no further command set the default cohort.

Options
-------

.. program:: pyam cohort




.. option:: -h, --help

   Show a help message and exit

.. option:: --list-students
    
    Print out student details (from students.csv)

.. option:: --list-files
    
    Print out file manifest (from manifest.json)

.. option:: --check-submissions
    
    Check student submissions listing missing files for each student.

.. option::  --list-tests
    
    Print out test information - either from test manifest or pytest collect


positional arguments
--------------------

.. option::   cohort
    
    Name of cohort to set as default or query