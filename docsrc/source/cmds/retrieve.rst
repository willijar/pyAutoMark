.. _Subcommand retrieve:

retrieve
========

Synopsis
--------

**pyam retrieve** [-h] [-c COHORT] [-s [STUDENTS [STUDENTS ...]]]

Description
-----------

:program:`pyam retrieve` retrieves files from student repositories on github (classroom).

    Cohort manifest be configured with:

       github.template: 
         The name of the template repository (prefix for student repositories)
    
       github.url: 
         URL to github organisation where repositories reside

    Students must have 'Github Username' field in csv file.

Options
-------

.. program:: pyam retrieve

.. option:: -h, --help

   Show a help message and exit

.. option::  -c COHORT, --cohort COHORT
    
    Name of cohort if different from current.

.. option::  -s [STUDENTS [STUDENTS ...]], --students [STUDENTS [STUDENTS ...]]
    
    List of specific students to process in cohort.