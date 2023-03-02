# pyAutoMark Todo List

* [X] Change setup to use toml file etc
* [X] An init command which produces a top level pyAutoAMrk.json file and fills it in from some questions
* [X] Test install and running under WIndows

## Bug Fixes

* [X] Mapping test ids to named cells - only letters, numbers and underscores allowed. Replacce other characters with Underscore - map
    Change in generate_template.py and mark.py
    >>> myre="[^a-zA-Z0-9_]+"
    >>> re.sub(myre,"_",s)[1:]


## Documentation

* [X] Document using sphinx - see <https://www.sphinx-doc.org/en/master/>
* [ ] Convert README to rst and copy into documentation sections
* [X] Write installation guide in rst
* [ ] Write documentation with use cases

## Major Features

## Improvements

* [ ] sort out timeout for tests - *test with timeout extension*
* [ ] Have configurable write-csv  which can also just create a csv file or produce mark from reports
* [ ] Capture errors only from vivado as feedback
