.. _Subcommand run:

run
===

Synopsis
--------

**pyam run** [-h] [-c COHORT] [-s [STUDENTS [STUDENTS ...]]] [--overwrite] [--prefix PREFIX] [-t TEST] [--new_only] [-m MARK]

Description
-----------

:program:`pyam run` run the test suite for specified cohort and students.

    It generates the test reports for each student in the reports folder.

Options
-------

.. program:: pyam run

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

.. option:: -t TEST, --test TEST
    
    Name of specific test to be run

.. option:: --new_only
    
    If set then only run tests for those student for whom there are no reports

.. option:: -m MARK, --mark MARK
    
    Selected marked tests when testing e.g. 'not slow' to not run slow tests