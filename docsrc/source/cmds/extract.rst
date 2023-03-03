.. _Subcommand extract:

extract
=======

Synopsis
--------

**pyam extract**  [-h] [-c COHORT] [-s [STUDENTS [STUDENTS ...]]] [--overwrite] [--prefix PREFIX] [--files ...]

Description
-----------

:program:`pyam extract` extracts student submissions from downloads files.

    Currently supports Blackboard GradeCenter download format where the downloaded file names
    contain the username and submission date.

Options
-------

.. program:: pyam extract

.. option:: -h, --help

   Show a help message and exit

.. option::  -c COHORT, --cohort COHORT
    
    Name of cohort if different from current.

.. option::  -s [STUDENTS [STUDENTS ...]], --students [STUDENTS [STUDENTS ...]]
    
    List of specific students to process in cohort.

.. option:: --overwrite
    
    If set overwrite existing output files.