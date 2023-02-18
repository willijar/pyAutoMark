# Copyright 2023, Dr John A.R. Williams
# SPDX-License-Identifier: GPL-3.0-only
"""Top level configuration for the assessment marking scripts"""
from pathlib import Path
import logging
import sys

#where tests are kept - this directory
TESTS_PATH = Path(__file__).resolve().parent
#Top level path - one above this
ROOT_PATH = TESTS_PATH.parent
#where cohorts submissions are kept
COHORTS_PATH = ROOT_PATH / "cohorts"
#directory for derived (build) files
BUILD_PATH = ROOT_PATH / "build"
#directory for reports
REPORTS_PATH = ROOT_PATH / "reports"

for path in (COHORTS_PATH, TESTS_PATH, BUILD_PATH, REPORTS_PATH):
    path.mkdir(exist_ok=True)

ERROR_LOG = logging.FileHandler(filename=BUILD_PATH / "error.log", mode='a')
ERROR_LOG.setLevel(logging.ERROR)
ERROR_LOG.setFormatter(
    logging.Formatter(
        '%(asctime)-12s: %(name)-8s: %(levelname)-8s: %(message)s',
        '%Y-%m-%d %H:%M:%S'))
## warning and above go to console - no need for time in format, log warning messages
CONSOLE = logging.StreamHandler()
CONSOLE.setLevel(level=logging.WARN)
CONSOLE.setFormatter(
    logging.Formatter('%(name)-8s: %(levelname)-8s %(message)s'))

log = logging.getLogger()
log.addHandler(ERROR_LOG)
log.addHandler(CONSOLE)

def handle_exception(exc_type, exc_value, exc_traceback):
    """Automatically handle uncaught exceptions via logger"""
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return
    log.critical(exc_value, exc_info=(exc_type, exc_value, exc_traceback))


sys.excepthook = handle_exception

#cohort logs infor and above
logging.getLogger("cohort").setLevel(logging.INFO)
