Quick Start
===========

pyAutoMark is an integrated tool to help 
with the automatic marking of electronically submitted students work. 
It can automate the retrieval or extraction of student work into directories,
the collection and running of unit tests for each student using the `pytest`_ framework
to produce reports that can be used for feedback, the summarising of these reports into
a marking spreadsheet for each student and finally the collection of those marks 
into  a csv file.

.. _`pytest`: https://docs.pytest.org/

This document proivdes a quick summary of how to carry out these tasks.

Once installed, pyAutoMark provides a console command :program:`pyam` which is used to
carry out the various tasks. You can type

.. code-block:: console

    $ pyam --help

to get the list of commands that are available

.. code-block:: console

    $ pyam <cmd> --help

to get help on a particular command.

The directory structure
-----------------------

pyAutoMark works within a directory structure as shown below. There is a :term:`root directory` 
which contains a configuration file :file:`pyAutoMark.json` which can be used to provided details
of your institution, department etc and configure many aspects of how pyAutoMark operates. puAutoMark operates on a 
:term:`cohort` which is a particular set of students doing a particular assignment.

pyAutoMark comes with a command :program:`pyam init` which sets up thisroot directory and configuration values
from a few questions it asks you. TO use this, run:

.. code-block:: console

    $ pyam init

| root
| ├─ pyAutoMark.json
| ├─ build
| ├─ cohorts
| │     ├─ cohort1
| │     │   ├─ manifest.json
| │     │   └─ students.csv
| │     └─ cohort2
| │        ├─ manifest.json
| │        └─ students.csv
| ├─ reports
| │     ├─ cohort1
| │     └─ cohort2
| └─ tests
|       ├─ cohort1
|       └─ cohort2


Setting up a cohort
-------------------

pyAutoMark needs two files providing information about the students in a cohort and the expected mainifest files.

students.csv
............

The student list should be provided as a csv file with, as a minimum, 
columns for the students "Last Name", "First Name", "Username" and "Student ID".
Below is an example of a csv which was directly dowloaded from the Blackboard VLE gradecentre.
It has the required information plus some extra headers which will be ignored.
The students.csv file may be updated by some operations of pyAutoMark,
for example a "Submission Date" field may be added if this can be determined from the student submission,
either from the last commit time to a github repositiory or from the submisison dowload filenames from Blackboard.

.. csv-table:: Example students.csv
    :header: Last Name,First Name,Username,Student ID,Last Access,Availability,Github Username

    Genius,Coyote,solution,0,2023-02-03 00::15:38,Yes,wiley1
    McTestFace,Testy,test,1,2023-02-03 00::15:38,Yes,testy1

For this example I have added a "Github Username" field which would be the students username on github if you are
using `Github Classroom`_ with these students. 

.. _Github Classroom: https://classroom.github.com/

manifest.json
..............

The second file which is needed for each cohort a json file with other information specific for this cohort. At a minimum 
it must at least contain a "files" section listing the files the students are expected to submit, 
and a description of that file as shown below e.g.

.. code-block:: json

    {
    "files": {
            "design.vhd": 
                {"description": "Description of design vhdl file"},
            "results.ghw": 
                {"description": "Results waveform file descritpion"}
        }
    "assessment": { "name": "Assessment Title" },
    "github": {
        "template": "my-practical",
        "url": "https://github.com/my-organisation/"
        }
    }

Other information that may vary for each :term:`cohort` may be provided here such as the name
and email address of the assessor, and assessment name and details to retrieve student work 
from github as shown above.

Setting up the tests
---------------------

You will also need to setup and write the tests which you want to apply fopr each :term:`cohort`.
These are stored in a folder with the same name as the cohort in the tests directory. pyAutoMark runs 
`pytest`_ to execute the set of tests in this folder for each student in the cohort,
collecting the output into a text file in the reports subdirectory. 
It provides fixtures for your `pytest`_ 
which are detailed in the :py:mod:`pyam.fixtures.common` module. 
Please read the `pytest`_ documentation for full details on how to write tests.

There are additional fixtures available to help with different types of tests - see :py:mod:`pyam.fixtures`
for the complete list.

The most useful fixtures which you may use in your tests are :py:attr:`pyam.fixtures.common.student` 
which refers to the :py:class:`pyam.cohort.Student` object you can use to refer to or find files for the current student, :py:func:`pyam.fixtures.common.test_path` 
which is the path to the directory in which the test files are kept
and :py:attr:`pyam.fixtures.common.build_path` which is the path
you can use for any temporary files generated during the test.

Retrieving the students work
----------------------------

Student submissions should be held in subdirectories of the :file:`cohort` subdirectory and named by the student username.
It you are using github classroom (recommended) and have configured the github details for the cohort then the command

.. code-block:: console

    $ pyam retrieve

will clone or pull the students work from their assignment repositories.

If you have downloaded the students work from a Blackboard assignment then the command

.. code-block:: console

    $ pyam extract --files ...

will parse the information in the given set of files and copy them into a directory for each student.
If the students have submitted archives (such as zip or tar.gz files) then the files will be extracted from the archives.

In both the above cases the student submission date will be added to the :file:`students.csv` file. You can query the
state of students with the command

.. code-block:: console

    $ pyam cohort --list-students


Running the tests
-----------------

The command 

.. code-block:: console

    $ pyam run

will execute all of the tests for each student and save the output from `pytest`_ into report files in the :file:`reports/cohort`` 
subdirectory. These will all be given a prefix (which can be specified with the --prefix argument) - it defaults to  "report\_".
These files can be sent to students as feedback - they will be particularly useful if you have given your tests meaningful names, 
and print any diagnostics mesages printed out by you test will be included in the reports.

Generating the mark spreadsheets
--------------------------------

You will often want to use the results of these tests to provide all or part of the mark for the students. 
To assist with this the results from the reports can be copied into a marking spreadsheet. The first step is to
generate a template spreadhseet which will then be filled in for each student.

The command


.. code-block:: console

    $ pyam generate-template

will produce a template spreadsheet for you in the :file:`reports/cohort subfolder` (with the specified filenanme prefix). 
This template will have have the test names and a result cell as a named reference which will be automatically filled in at the mark stage.
The Named cell references for each test which will be marked as either "PASSED" or "FAILED"
from the `pytest`_ report file. The generate template is intended as a starting point for you to modify with your 
own marking shceme which might, for example, include manual entered evaluation, and provided a weighting for each test result.

Once you are happy with your marking sheet type the command


.. code-block:: console

    $ pyam mark

And a marking spreadsheet will be produced for each student in the :file:`reports/cohort subfolder` 
(with the specified filename prefix). You can then add in you manual elements

And finally - collating the marks
---------------------------------

The command

.. code-block:: console

    $ pyam write-csv --csv-files ....

will read the marks from the finished marked spreadshsset for each student and entern them into the given speadsheet csv files.





















