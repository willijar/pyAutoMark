.. _Subcommands:

Commands
========

Synopsis
--------

**pyam** [-h] {run,retrieve,extract,mark,generate-template,find-duplicates,config,cohort,write-csv,init} ..

Description
-----------

:program:`pyam` is an integrated tool to automatically retrieve, mark and provide feedback
for digital student submissions.

It takes a number of subcommands to carry out the different activities.


Options
-------

.. program:: pyam

.. option:: -h, --help

   Show a help message and exit

.. option::  {run,retrieve,extract,mark,generate-template,find-duplicates,config,cohort,write-csv,init}

    The specific subcommand to execute as follows:

    :ref:`run<Subcommand run>`          
    
        Run the test suite for specified cohort and students

    :ref:`retrieve<Subcommand retrieve>`
    
        Retrieve files from student repositories on github (classroom).
    
    :ref:`extract<Subcommand extract>`

        Extract student submissions from downloads files
    
    :ref:`mark<Subcommand mark>`

        Generate mark spreadsheets for each student

    :ref:`generate-template<Subcommand generate-template>`

       Generate a template marking spreadsheet
    
    :ref:`find-duplicates<Subcommand find-duplicates>`

        Find duplicate files from students across cohorts
    
    :ref:`config<Subcommand config>`

        Set or query configuration parameters.
    
    :ref:`cohort<Subcommand cohort>`

        Set or query cohort information.
    
    :ref:`write-csv<Subcommand write-csv>`

        Read marks from a set of mark spreadsheets and write them into csv files
    
    :ref:`init<Subcommand init>`
    
        Initialise a directory for pyAutoMark


