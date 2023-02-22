# pyAutoMark Todo List

## Documentation

* [X] Document using sphinx - see <https://www.sphinx-doc.org/en/master/>
* [ ] COnvert README to rst
* [ ] Write installation guide in rst
* [ ] Write documentation with use cases
* [ ] Tidy up in app help before files commited

## Bug Fixes

## Features

* [X] Add in linting (for C and Python) as relevant fixtures e.g.
     clang-tidy Q2b.c -checks=* -- -I../../../tests/2022/ -- stderr has 70 warnings generated and stdout has warnings list
     pylint filename
* [ ] cohort  command tpo checkout cohorts and list students/files/submissions
* [ ] Student query command (maybe using config cohort.student as special case)

## Improvements

* [X] Tidy up file finding - single interface in student and fixtures
* [X] Add options in files manifest and module fo find files by "matching" and "contains" options (contains assumes file name is a match)
* [X] Rename fixture sets
* [X] Use import pyAutoMark.gsgg (or whatever will work - create pyAutoMark subdirectory for package which can go anywhere?)
* [X] Config class reads json  using data class
* [X] File finding using matching patterns -in manifest and in tests - student.file(filename), student.file_matches(glob or regext), student.file_contains(regexp)
