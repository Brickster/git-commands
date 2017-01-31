#! /bin/bash
set -ev

# upload coverage report for pushes to master only
# NOTE: secure environment variables aren't available for PRs from other repositories
if [[ ! -z "$CODACY_PROJECT_TOKEN" ]]; then
    coverage xml --include=bin/* --omit=*/__init__.py -o coverage.xml
    # python-codacy-coverage --commit "$TRAVIS_COMMIT" --report coverage.xml
    echo "$TRAVIS_COMMIT"
    python-codacy-coverage --report coverage.xml
fi
