.. _Subcommand config:

config
======

Synopsis
--------

**pyam config**  [-h] [--type TYPE] key [value]

Description
-----------

:program:`pyam config` Set or query configuration parameters.

    Keys may be in '.' format e.g. 2022.assessor.username sets assessor.username in cohort 2022
    global name may be used to set global parameters across all cohorts (unless set locally).
    If no value is given print out current value.

Options
-------

.. program:: pyam config

.. option:: -h, --help

   Show a help message and exit

.. option:: --type TYPE  
    
    Type conversion to perform on value e.g. int,float
    
    Name of cohort if different from current.

Positional arguments
--------------------

.. option::  key
    
    Key of value to be set in '.' format e.g. assessor.username

.. option:: value
    
    value to be set (if no value give output current value)
