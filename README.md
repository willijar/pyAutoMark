# Automated marking and feedback

## Applicability

This toolset is applicable for all assessments (coursework, practical work, exams and class tests ) where students
are required to submit their work electronically and where the submission can be analysed electronically e.g.

* Software which can be tested using unit testing (in any language).
* Embedded Systems which can be tested using mock libraries and headers instead of the hardware
* Digital desines using a hardware description language (e.g. VHDL) whic can be tested in simulation or synthesis
* Data files which can be read and analysed - these might br created from simulations, or experimental measurements
  or data recorded from test instruments
* Spreadhseet files which might be used to capture student readings and answers to questions.

The toolset is written in Python and can run on almost any Platform - PCs, Linux or Mac.
Users will need to isntall other software needed for the actual tests such as C compilers
for host and embedded C applications, VHDL simulators and synthesis tools, Python libraries etc.

## Process and Coverage

The toolset automates the following steps

1. Collation of student work into folders for a cohort/assessment.
   This may be from a Blackboard dump of files and archives from grade centre or (preferred)
   the cloning and pulling of student work from github classroom repositories.

2. The collation and use  of student information from a provided csv file (e.g. downloaded from Blackboard)

3. Checking of student submission against a manifest of expected files (provided)

4. The collation of a set of tests to be run against the students work - these can be almost anything (see applicability above).

5. The automated running of the tests across a cohort or set of students amd the collection of the results into a feedback report.

6. The generation of a marking template based on the set of tests - this may then be added
   to as necessary to integrate different marking schemes and non-automated marking results.

7. The generation of completed marking sheets for the students (using the report data and a template marking sheet)

8. The sending out by email of the marking sheets and reports to students (work in progress)

9. The automated filling in of a csv file from the marking sheet for sending marks to the office.

## Requirements

### Software

| Software                 | Min Version |  Link                                                      |
|--------------------------|-------------|------------------------------------------------------------|
| Visual Studio Code       | 1.74.2      | <https://code.visualstudio.com/> |
| Python                   | 3.10.9      | <https://www.python.org/downloads/windows/>  |
| pytest                   | 7.2.1       | pip install pytest |
| git                      | 2.39.0.windows.2 | <https://gitforwindows.org/> |

### Common ComponentsLibraries

| Python Libraries         | Version     |
|--------------------------|-------------|
| openpyxl                 | 3.0.10      |

| VSCode Extensions        | Author      |
|--------------------------|-------------|
| C/C++                    | Microsoft   |
| C/C++ Extension Pack     | Microsoft   |
| Python Test Explorer     | Little Fox Team |
| Github Classroom         | Github      |

## TODO

* Test/sort so tests can be in separate folder to pyAutoMark
* Add in Python fixtures and test with EE1CPS
* Add in linting (for C and Python) as relevant fixtures
* File finding using matching patterns -in manifest and in tests
