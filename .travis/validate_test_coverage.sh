#! /bin/bash
#
# Validate that test coverage reaches the required minimum. A non-zero exit status means coverage is too low.
#
set -ev

coverage_percent=$(coverage report --include=bin/* --omit=*/__init__.py | egrep "TOTAL" | awk '{print $NF}')
if [[ "$coverage_percent" != "100%" ]]; then
    exit 1
fi
