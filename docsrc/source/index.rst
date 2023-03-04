Welcome to pyAutoMark
=====================

.. epigraph:: pyAutoMark simplifies automating your marking and feedback

Here are pyAutoMark's major features:

* **Collection:**  Collection and collation of student work into folders for a cohort/assessment.
   This may be from a Blackboard dump of files and archives from grade centre or (preferred)
   the cloning and pulling of student work from `Github Classroom`_ repositories.

* **Testing:** It builds upon the `pytest`_` testing framework to collect and run tests against each student submission.

* **Feedback:** The results of the tests are collected feedback reports per student which list the tests failed
  and guidance on what what was wrong. These can then be  used to fill in marking spreadsheets.

* **Flexibility:** Tests can be anything that can be tested or measured using software. Some examples include

  * Software unitests in any language (not just Python, but C or even VHDL simulation and synthesis
    for hardware desing)

  * Measured data measured from instruments in a practical or generated from simulations. 

  * Student provided answers in a spreadsheet.

  * A memory dump output from a debugger on an embedded system.

* **Extendable:** `pytest fixtures`_ are extensively used to enable customisation and extension. Provided fixtures
  which student files are tested and where the result should be reported. Additional sets provided
  for specific use cases such as using mock C testing for checking embedded systems desing (e.g. AVR),
  Python code and VHDL designs.

* **Marking Templates**: A template marking spreadsheet can be automatically generated from the set 
  of tests. This can then be customised and added to either with your own marking scheme or
  to including manual input for those aspects which cannot be automatically marked

* **Multiple Assessments**: pyAutoMark manages a directory heirachy to accomodate multiple assignments or
  cohorts of students.

* **Student management**: pyAutoMark uses a simple csv file of student details which can be provided e.g. from Blackboard.
  It can provide reports on who has submitted, and when, and if they have missed a deadline.
  When combined with `Github Classroom`_ this provides a very effective
  mechanism to monitor student engagement.

* **Logging**: Most activities on a cohort or assessment are logged to provide a historic record.

* **Mark Collection**: Marks from the marking spreadsheets can be collated into a csv file for
  adminsitrative purposes such as sending to the office.

.. _pytest: https://pytest.org/

.. _pytest fixtures: https://docs.pytest.org/en/6.2.x/fixture.html

.. _Github Classroom: https://classroom.github.com/

Getting Started
---------------

The basics of installing and getting started using pyAutoMark
including setting up your directory structure for submissions, reports and tests.

.. toctree::
   :maxdepth: 2

   installation
   quickstart

Subcommands
-----------

The :program:`pyam` program subcommands

.. toctree::
   :maxdepth: 1
   :glob:

   cmds/*

Examples of Use
---------------

.. toctree::
   :maxdepth: 1

   Embedded C <examples/cmock>

Reference Guide
---------------

A complete collection of reference information.

.. toctree::
   :maxdepth: 2

   modules

   glossary


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
