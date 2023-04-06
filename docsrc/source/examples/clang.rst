.. _example C:

C
=

pyAutoMark can detect simple C unit test files in the tests directory.

.. highlight:: c

Directory structure
-------------------

Below is the directory structure for these tests. Under the cohort directory we will have a directory for each student which will
contain their submitted code - in this case :file:`Q1.c` and :file:`Q2.c`. In our tests folder for the cohort we have the C unit test files :file:`test1_Q1.c`, :file:`test1_Q1.c` etc. The
unittes files must start with "test\_" and must contain some definitions to be recognised as test files.

| root
| ├─ cohorts
| │     ├─ cohort1
| │     │   └─ student1
| │     │   │  └─ Q1.c
| │     │   │  └─ Q2.c
| └─ tests
| │     └─ test_Q1.c
| │     └─ test_Q2.c

The clang fixtures provided by pyAutoMark will set up the compilation include directories to point to the appropriate test folder and student folder. Compilation is performed as one unit with the students file included automatically at the beginning of the unit test C file.

To be collected the C test filenames must start with "test\_" and contain
the following definitions

:PYAM_TEST: A unix glob string used to find the students file under test.

:PYAM_TIMEOUT: (Optional) A floating point value spcifying the timeout for these tests.

:PYAM_LINT: (Optional) A number specifying the naximum number of LINT warnings allowed
    for the test to pass and optionally followed by the list of LINT checks to perform

e.g.

.. code-block:: C

    #DEFINE PYAM_TEST "UUT.c"
    #DEFINE PYAM_LINT N,CHECKS
    #DEFINE PYAM_TIMEOUT TIMEOUT

.. option:: UUT.c

    The filename glob in the students directory 

.. option:: N

    The number of warnings to allow before a lint check is considered a fail.

.. option:: CHECKS

    The list fo checks (passed to clang-tidy)

.. option:: TIMEOUT

    THe maximum run time for a test in seconds.

For each test that we want to perform this code will be compiled and and then executed with a different definition set using the -d argument on the compiler. We therefore use :code:`#ifdef` or :code:`#ifdefined` blocks in the C program
to select which test we want to carry out. To be recognised as tests the definitions must start with with "TEST\_". e.g.

.. code-block:: C

    #ifdefined TEST_MYTEST
    // Your test code here
    #endif


