# pyAutoMark Todo List

* [ ] Setup and install from directory using pip
* [ ] Test under Windows (using c-mock example)
* [ ] Test and install from github

## Bug Fixes

## Documentation

* [X] Document using sphinx - see <https://www.sphinx-doc.org/en/master/>
* [ ] Convert README to rst and copy into documentation sections
* [ ] Write installation guide in rst
* [ ] Write documentation with use cases
* [ ] Tidy up in app help before files commited

## Major Features

## Improvements

* [X] Factor out commands to cmd and change add_common_args to allow selection
* [X] sort out timeout for tests
* [X] Use names in template-template for begin of marks, university, course and assessment fields and use prefix
* [ ] An init command which produces a top level pyAutoAMrk.json file and fills it in from some questions
* [ ] A write-csv command which will read marks from mark spreadsheets and enter them into csv files
* [X] Have unviersty, course and assessment as config fields filled into template spreadsheet
* [X] Have template-template.xlsx as a configuration parameter (and if not specified copy into reports folder upon init)
* [X] Have commands in separate folder so they can be iterated over in pyAutoMark.py
