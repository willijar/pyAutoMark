import pytest

def test_manifest(student):
    "Tests if current student has all files listed in cohort manifest"
    missing=student.check_manifest()
    if missing: raise FileNotFoundError(missing)