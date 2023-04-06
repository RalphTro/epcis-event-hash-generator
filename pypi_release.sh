#!/bin/bash
#
# Build the package and release to PyPI. Then clean up the artefacts.

set -e

PYTHON=python3

cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1

echo "Publishing Package from $(pwd)"

echo
echo -e "[...]\t testing"
$PYTHON -m pip install -r requirements.txt
flake8
cd tests
pytest
cd ..
#$PYTHON -m pip install -e .
echo -e "[ok]\t testing"

echo
echo -e "[...]\t building"
$PYTHON -m pip install --upgrade setuptools
$PYTHON setup.py sdist
$PYTHON -m pip install --upgrade wheel
$PYTHON setup.py bdist_wheel --universal
echo -e "[ok]\t building"

echo
echo -e "[...]\t uploading to PyPI"
$PYTHON -m pip install --upgrade twine
$PYTHON -m twine upload dist/*
echo -e "[ok]\t uploaded"
echo
echo -e "[...]\t installing from PyPI via"
COMMAND="$PYTHON -m pip install epcis_event_hash_generator"
echo $COMMAND
echo
$COMMAND
echo -e "[ok]\t installing works"

echo
echo -e "[...]\t removing artefacts"
rm -rf *.egg-info
rm -rf build
rm -rf dist
echo -e "[ok]\t removing artefacts"

echo
echo "☑️"
echo
