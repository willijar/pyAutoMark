# pyAutoMark Todo List

## Documentation

* [X] Document using sphinx - see <https://www.sphinx-doc.org/en/master/>
* [ ] Write installation guide in rst
* [ ] Write documentation with use cases
* [ ] Tidy up in app help before files commited

## Bug Fixes

## Features

* [ ] test on windows
* [ ] make pip installable using  setuptools - see <https://betterscientificsoftware.github.io/python-for-hpc/tutorials/python-pypi-packaging/>
* [X] Add in linting (for C and Python) as relevant fixtures e.g.
     clang-tidy Q2b.c -checks=* -- -I../../../tests/2022/ -- stderr has 70 warnings generated and stdout has warnings list
     pylint filename
* [X] cohort  command tpo checkout cohorts and list students/files/submissions
* [X] Student query command (maybe using config cohort.student as special case)
* [X] github retrieve update submission date "git log -1 --format=%cd" -> datetime.strptime("Wed Feb 22 08:03:06 2023 +0000","%a %b %d %H:%M:%S %Y %z")
* [X] Dislay submission dates, days late and days ago for students

## Improvements

* [X] Tidy up file finding - single interface in student and fixtures
* [X] Add options in files manifest and module fo find files by "matching" and "contains" options (contains assumes file name is a match)
* [X] Rename fixture sets
* [X] Use import pyAutoMark.gsgg (or whatever will work - create pyAutoMark subdirectory for package which can go anywhere?)
* [X] Config class reads json  using data class
* [X] File finding using matching patterns -in manifest and in tests - student.file(filename), student.file_matches(glob or regext), student.file_contains(regexp)
