Configuration
-------------

The operation of pyAutoMark is highly customisable with a number of parameters that can be set
either at the toplevel, in the top level :file:`pyAutoMark.json` file, or for each cohort in the :file:`manifest.json` file in the cohort directory. 
These json files can be edited manually, or the parameters may be set using the :ref:`config<Subcommand config>` command.

Configuration Keys may be in a '.' format e.g. 2022.assessor.username sets assessor.username in cohort 2022.
global name may be used to set global parameters across all cohorts (unless set locally).

Configuration Parameters
========================

The heirarchical list of configurable parameters is given below.

.. include:: schema.rst

