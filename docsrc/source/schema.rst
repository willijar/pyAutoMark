Configuration Parameters
========================

:assessor:
    :email: assessor's email address
    :name: assessor's name
:course:
    :code: code for module/course
    :name: title for module/course
:institution:
    :name: name of institution
    :department: name of department
    :domain: domain to add to usernames for email
:github:
    :url: url for organisation on github (if applicable)
    :assignment: Title of github assignment (prefix for student repositories)
:fixtures: List of pytest fixture sets to use
:path:
    :tests: (Path) file path to tests - default: 'tests'
    :build: (Path) file path to build directory for temporary files - default: 'build'
    :cohorts: (Path) file path to directory for cohort/student submissions - default: 'cohorts'
    :reports: (Path) file path for reports - default: 'reports'
:deadline: (fromisoformat) deadline for assessment submission
