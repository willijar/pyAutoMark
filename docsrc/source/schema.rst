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
    :branch: Name of default branch to use in student's repositories - default: 'main'
:fixtures: (list) List of pytest fixture sets to use
:path:
    :tests: (Path) file path to tests - default: 'tests'
    :build: (Path) file path to build directory for temporary files - default: 'build'
    :cohorts: (Path) file path to directory for cohort/student submissions - default: 'cohorts'
    :reports: (Path) file path for reports - default: 'reports'
:deadline: (datetime) deadline for assessment submission
:student-folder-name: What field to use for students folder name - default: 'username'
:filematch:
    :pattern: How to match/search for students files - one off exact, glob or regexp. - default: 'glob'
:solution:
    :username: Username for 'solution' student in cohort
:workbook: Name/relative path to students workbook for xlsx fixtures
:student-column:
    :studentid: The column to read for studentid - default: '(?i)Student\s*ID'
    :username: Column to read for students username - default: '(?i)Username'
    :lastname: Column to read for students last (family) name - default: '(?i)Last\s*name'
    :firstname: Column to read for students first (given) name - default: '(?i)First\s*name'
    :course: Column to read specifying which course student is on (if different from default) - default: '(?i)Child Course ID'
    :github-username: Column to read for the students username on github - default: '(?i)Github Username'
    :submission-date: Column name to use to record submission dates - default: 'Submission Date'
    :extension: Column name to use for student extensions - default: 'Extension'
:mark-column:
    :studentid: Column name in marking csv file with student id - default: '#Cand Key'
    :mark: Column name in marking csv file for mark - default: 'Mark'
:template:
    :report: Name of cell in marking template for report - default: 'report'
