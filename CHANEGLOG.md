# Change Log for pyAutoMark

## v0.3.2

* fix c_exec issue with timeout
* Change to use toml file for setup
* Initial implementation init command
* Add config SCHEMA
* Rename script to pam.py
* Refactor ConfigManager to separate file
* Initial implementation write-csv cmd
* Add check that report for marking is .txt file
* Add pytest-timeout to requirements
* Fix config lookup

## v0.3.1

* Fix missing template-template.xlsx from package data

## v0.3.0

* Configured setup.py for installation
* Update Requirements
* Add timeout marker
* Use DefineNames for temaplte.xlsx generation
* Factored commands into cmd package
* Tidy subprocess.run calls
* Top level help now derived from main.__doc__ in subcommands
* Minor Update for Windows compatibility (use ; in path rather than:)
* Provide student submission details listing from cohort command
* Add in cohort command with options
* Factor out run_pytest
* Move documentation to separate docs branch
* Start documentation of package
* Fixtures can be named in config (all by default)
* Refactor modules into pyam package
* Factor TODO to separate file from README
* Impove doc strings
* Make Cohort subclass of ConfigManager
* Add python_lint fixture
* Add c lint fixture using clang-tidy

## v0.2.0

* Add Python module test fixtures
* Add check submission subcommand
* Linted and tidied source code
* Default cohort can now be set as global parameter
* Add ConfigManager class for configuration
* Add top level pyAutoMark command


## v0.1.0:  Initial commit

